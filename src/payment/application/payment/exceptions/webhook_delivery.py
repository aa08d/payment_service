from typing import ClassVar

from payment.application.common.exceptions import ApplicationError


class WebhookDeliveryError(ApplicationError):
    status: ClassVar[int] = 502

    def __init__(self, url: str) -> None:
        self._url = url

    @property
    def message(self) -> str:
        return f"Webhook delivery to {self._url} failed"
