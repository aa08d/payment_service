import logging
from dataclasses import dataclass
from uuid import UUID

from payment.application.common.commands import Command, CommandHandler
from payment.application.common.interfaces import UnitOfWork
from payment.application.common.mediator import Mediator
from payment.application.payment.exceptions import PaymentNotExistsError
from payment.application.payment.interfaces import PaymentGateway
from payment.domain.payment.repositories import PaymentRepository
from payment.domain.payment.value_objects import PaymentID

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessPaymentCommand(Command[None]):
    payment_id: UUID


class ProcessPaymentHandler(CommandHandler[ProcessPaymentCommand, None]):
    def __init__(
        self,
        payment_repository: PaymentRepository,
        gateway: PaymentGateway,
        uow: UnitOfWork,
        mediator: Mediator,
    ) -> None:
        self._payment_repository = payment_repository
        self._gateway = gateway
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: ProcessPaymentCommand) -> None:
        payment_id = PaymentID(command.payment_id)
        payment = await self._payment_repository.acquire_by_id(payment_id)

        if payment is None:
            raise PaymentNotExistsError(command.payment_id)

        if payment.status.is_terminal:
            logger.info(
                "Payment already processed, skipping",
                extra={
                    "payment_id": command.payment_id,
                    "status": payment.status.value,
                },
            )
            return

        decision = await self._gateway.process(
            payment_id=payment.payment_id.value,
            amount=payment.money.amount,
            currency=payment.money.currency.value,
        )

        if decision.approved:
            payment.succeed()
        else:
            payment.fail()

        await self._mediator.publish(payment.pull_events())
        await self._uow.commit()

        logger.info("Payment processed", extra={"payment_id": command.payment_id, "status": payment.status.value})
