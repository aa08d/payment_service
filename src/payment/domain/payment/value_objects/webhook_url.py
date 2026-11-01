from dataclasses import dataclass
from urllib.parse import urlsplit

from payment.domain.common.exceptions import DomainError
from payment.domain.common.value_objects import ValueObject

ALLOWED_SCHEMES = frozenset({"http", "https"})


class WebhookURLError(DomainError):
    pass


class InvalidWebhookURLError(WebhookURLError):
    def __init__(self, url: str) -> None:
        self.url = url

    @property
    def message(self) -> str:
        return f"Invalid webhook URL: {self.url!r}."


@dataclass(frozen=True)
class WebhookURL(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or any(char.isspace() for char in self.value):
            raise InvalidWebhookURLError(self.value)

        parts = urlsplit(self.value)

        if parts.scheme not in ALLOWED_SCHEMES or not parts.hostname:
            raise InvalidWebhookURLError(self.value)

        _, separator, raw_port = parts.netloc.rpartition(":")

        if separator and (not raw_port.isdigit() or not 1 <= int(raw_port) <= 65_535):
            raise InvalidWebhookURLError(self.value)
