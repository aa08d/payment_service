from abc import ABC, abstractmethod

from payment.domain.payment.entities import Payment
from payment.domain.payment.value_objects import IdempotencyKey, PaymentID


class PaymentRepository(ABC):
    @abstractmethod
    async def acquire_by_id(self, payment_id: PaymentID) -> Payment | None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, payment: Payment) -> None:
        raise NotImplementedError

    @abstractmethod
    async def acquire_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment:
        raise NotImplementedError
