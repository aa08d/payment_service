import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.application.common.commands import Command, CommandHandler
from payment.application.common.interfaces import UnitOfWork
from payment.application.common.mediator import Mediator
from payment.application.payment.dto import CreatePaymentDTO
from payment.application.payment.exceptions import IdempotencyKeyAlreadyExistError, IdempotencyKeyConflictError
from payment.domain.payment.entities import Payment
from payment.domain.payment.repositories import PaymentRepository
from payment.domain.payment.value_objects import Description, IdempotencyKey, WebhookURL
from payment.domain.payment.value_objects.money import Currency, Money

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreatePaymentCommand(Command[CreatePaymentDTO]):
    idempotency_key: UUID
    amount: Decimal
    currency: Currency
    description: str
    webhook_url: str
    metadata: dict[str, Any]


class CreatePaymentHandler(CommandHandler[CreatePaymentCommand, CreatePaymentDTO]):
    def __init__(
        self,
        payment_repository: PaymentRepository,
        uow: UnitOfWork,
        mediator: Mediator,
    ) -> None:
        self._payment_repository = payment_repository
        self._uow = uow
        self._mediator = mediator

    async def __call__(self, command: CreatePaymentCommand) -> CreatePaymentDTO:
        idempotency_key = IdempotencyKey(command.idempotency_key)
        money = Money(command.amount, command.currency)
        description = Description(command.description)
        webhook_url = WebhookURL(command.webhook_url)

        payment = Payment.create(
            idempotency_key=idempotency_key,
            money=money,
            description=description,
            webhook_url=webhook_url,
            metadata=command.metadata,
        )

        try:
            await self._payment_repository.save(payment)
        except IdempotencyKeyAlreadyExistError as err:
            await self._uow.rollback()

            existing = await self._payment_repository.acquire_by_idempotency_key(idempotency_key)

            same_request = (
                existing.money == money
                and existing.description == description
                and existing.webhook_url == webhook_url
                and existing.metadata == command.metadata
            )

            if not same_request:
                raise IdempotencyKeyConflictError(command.idempotency_key) from err

            return CreatePaymentDTO(
                payment_id=existing.payment_id.value,
                status=existing.status.value,
                created_at=existing.timestamps.created_at,
            )

        await self._mediator.publish(payment.pull_events())
        await self._uow.commit()

        logger.info(
            "Payment created",
            extra={"payment_id": payment.payment_id.value, "idempotency_key": command.idempotency_key},
        )

        return CreatePaymentDTO(
            payment_id=payment.payment_id.value,
            status=payment.status.value,
            created_at=payment.timestamps.created_at,
        )
