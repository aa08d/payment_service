from uuid import UUID

from payment.application.payment.dto import PaymentDetailDTO
from payment.application.payment.interfaces.persistence import PaymentReader


class PaymentReaderMock(PaymentReader):
    def __init__(self) -> None:
        self.payments: dict[UUID, PaymentDetailDTO] = {}

    async def get_payment_by_id(self, payment_id: UUID) -> PaymentDetailDTO | None:
        return self.payments.get(payment_id)

    async def add_payment(self, payment: PaymentDetailDTO) -> None:
        self.payments[payment.payment_id] = payment
