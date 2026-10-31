from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from payment.application.common.dto import DTO


@dataclass(frozen=True)
class CreatePaymentDTO(DTO):
    payment_id: UUID
    status: str
    created_at: datetime
