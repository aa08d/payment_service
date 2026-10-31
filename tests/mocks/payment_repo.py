from payment.application.payment.exceptions import IdempotencyKeyAlreadyExistError
from payment.domain.payment.entities import Payment
from payment.domain.payment.repositories import PaymentRepository
from payment.domain.payment.value_objects import IdempotencyKey, PaymentID


class PaymentRepositoryMock(PaymentRepository):
    def __init__(self) -> None:
        self.payments: dict[PaymentID, Payment] = {}

    async def acquire_by_id(self, payment_id: PaymentID) -> Payment | None:
        return self.payments.get(payment_id)

    async def acquire_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment:
        for payment in self.payments.values():
            if payment.idempotency_key == idempotency_key:
                return payment
        raise LookupError(idempotency_key)

    async def save(self, payment: Payment) -> None:
        # The real repository fails on flush because of the unique constraint on the idempotency key
        if any(saved.idempotency_key == payment.idempotency_key for saved in self.payments.values()):
            raise IdempotencyKeyAlreadyExistError(payment.idempotency_key.value)
        self.payments[payment.payment_id] = payment
