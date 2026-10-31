from enum import StrEnum

from payment.domain.common.exceptions import DomainError


class PaymentStatusError(DomainError):
    pass


class InvalidStatusTransitionError(PaymentStatusError):
    def __init__(self, current: str, target: str) -> None:
        self._current = current
        self._target = target

    @property
    def message(self) -> str:
        return f"Invalid payment status transition: {self._current} -> {self._target}"


class PaymentStatus(StrEnum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"

    @classmethod
    def create(cls) -> PaymentStatus:
        return cls.pending

    def succeed(self) -> PaymentStatus:
        return self._to(PaymentStatus.succeeded)

    def fail(self) -> PaymentStatus:
        return self._to(PaymentStatus.failed)

    @property
    def is_pending(self) -> bool:
        return self is PaymentStatus.pending

    @property
    def is_terminal(self) -> bool:
        return self in (PaymentStatus.succeeded, PaymentStatus.failed)

    def _to(self, status: PaymentStatus) -> PaymentStatus:
        if self is not PaymentStatus.pending:
            raise InvalidStatusTransitionError(self.value, status.value)

        return status
