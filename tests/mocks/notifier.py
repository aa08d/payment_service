from payment.application.payment.dto import PaymentDetailDTO
from payment.application.payment.interfaces import WebhookNotifier


class WebhookNotifierMock(WebhookNotifier):
    def __init__(self) -> None:
        self.error: Exception | None = None
        self.notified: list[PaymentDetailDTO] = []

    async def notify(self, payment: PaymentDetailDTO) -> None:
        if self.error is not None:
            raise self.error
        self.notified.append(payment)
