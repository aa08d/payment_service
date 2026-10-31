from typing import Protocol

from payment.application.payment.dto import PaymentDetailDTO


class WebhookNotifier(Protocol):
    async def notify(self, payment: PaymentDetailDTO) -> None:
        raise NotImplementedError
