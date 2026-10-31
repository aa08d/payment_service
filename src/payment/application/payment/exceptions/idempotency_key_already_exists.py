from typing import ClassVar
from uuid import UUID

from payment.application.common.exceptions import ApplicationError


class IdempotencyKeyConflictError(ApplicationError):
    status: ClassVar[int] = 409

    def __init__(self, idempotency_key: UUID) -> None:
        self._idempotency_key = idempotency_key

    @property
    def message(self) -> str:
        return f"Idempotency key {self._idempotency_key} was already used with different request parameters."


class IdempotencyKeyAlreadyExistError(ApplicationError):
    def __init__(self, idempotency_key: UUID) -> None:
        self._idempotency_key = idempotency_key

    @property
    def message(self) -> str:
        return f"Payment with idempotency key {self._idempotency_key} already exists."
