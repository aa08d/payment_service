from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

from payment.domain.common.exceptions import DomainError
from payment.domain.common.value_objects import ValueObject


class PaymentTimestampsError(DomainError):
    pass


class PaymentAlreadyProcessedError(PaymentTimestampsError):
    def __init__(self, processed_at: datetime) -> None:
        self._processed_at = processed_at

    @property
    def message(self) -> str:
        return f"Payment was already processed at {self._processed_at.isoformat()}"


@dataclass(frozen=True)
class PaymentTimestamps(ValueObject):
    created_at: datetime
    processed_at: datetime | None

    @classmethod
    def create(cls) -> Self:
        now = datetime.now(UTC)
        return cls(created_at=now, processed_at=None)

    def mark_processed(self) -> PaymentTimestamps:
        if self.processed_at is not None:
            raise PaymentAlreadyProcessedError(self.processed_at)

        now = datetime.now(UTC)
        return PaymentTimestamps(
            created_at=self.created_at,
            processed_at=now,
        )
