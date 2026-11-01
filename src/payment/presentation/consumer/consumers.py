import logging
from abc import ABC, abstractmethod
from typing import ClassVar
from uuid import UUID

from dishka import AsyncContainer
from faststream.rabbit import RabbitMessage

from payment.application.common.mediator import Mediator
from payment.application.payment.commands import ProcessPaymentCommand
from payment.application.payment.events import SendWebhookEvent
from payment.infrastructure.message_broker.retry import MessageRetrier
from payment.infrastructure.message_broker.topology import NEW_PAYMENTS_QUEUE, WEBHOOK_QUEUE

from .messages import PaymentMessage

logger = logging.getLogger(__name__)


class PaymentConsumer(ABC):
    queue: ClassVar[str]

    def __init__(self, container: AsyncContainer, retrier: MessageRetrier) -> None:
        self._container = container
        self._retrier = retrier

    async def handle(self, body: PaymentMessage, message: RabbitMessage) -> None:
        attempt = self._retrier.attempt_of(message)
        payment_id = body.payment_id

        try:
            async with self._container() as request_container:
                mediator = await request_container.get(Mediator)
                await self._execute(mediator, payment_id)
        except Exception as err:
            logger.warning(
                "Payment message failed",
                extra={"queue": self.queue, "payment_id": payment_id, "attempt": attempt, "error": repr(err)},
                exc_info=err,
            )
            await self._retrier.retry_or_dead_letter(self.queue, message, attempt, err)
            return

        logger.info(
            "Payment message handled",
            extra={"queue": self.queue, "payment_id": payment_id, "attempt": attempt},
        )

    @abstractmethod
    async def _execute(self, mediator: Mediator, payment_id: UUID) -> None:
        raise NotImplementedError


class ProcessPaymentConsumer(PaymentConsumer):
    queue = NEW_PAYMENTS_QUEUE

    async def _execute(self, mediator: Mediator, payment_id: UUID) -> None:
        await mediator.send(ProcessPaymentCommand(payment_id=payment_id))


class SendWebhookConsumer(PaymentConsumer):
    queue = WEBHOOK_QUEUE

    async def _execute(self, mediator: Mediator, payment_id: UUID) -> None:
        await mediator.publish(SendWebhookEvent(payment_id=payment_id))
