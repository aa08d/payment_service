from typing import Protocol
from uuid import UUID

from payment.application.payment.dto import PaymentDetailDTO


class PaymentReader(Protocol):
    async def get_payment_by_id(self, payment_id: UUID) -> PaymentDetailDTO | None:
        raise NotImplementedError
