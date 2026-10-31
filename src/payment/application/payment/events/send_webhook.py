import logging
from dataclasses import dataclass
from uuid import UUID

from payment.application.common.events import EventHandler
from payment.application.payment.exceptions import PaymentNotExistsError
from payment.application.payment.interfaces import WebhookNotifier
from payment.application.payment.interfaces.persistence import PaymentReader
from payment.domain.common.events import Event

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SendWebhookEvent(Event):
    payment_id: UUID


class SendWebhookHandler(EventHandler[SendWebhookEvent]):
    def __init__(self, payment_reader: PaymentReader, notifier: WebhookNotifier) -> None:
        self._payment_reader = payment_reader
        self._notifier = notifier

    async def __call__(self, event: SendWebhookEvent) -> None:
        payment = await self._payment_reader.get_payment_by_id(event.payment_id)

        if payment is None:
            raise PaymentNotExistsError(event.payment_id)

        await self._notifier.notify(payment)

        logger.info("Webhook delivered", extra={"payment_id": payment.payment_id, "status": payment.status})
