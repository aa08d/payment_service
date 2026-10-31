from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.application.common.dto import DTO


@dataclass(frozen=True)
class PaymentDetailDTO(DTO):
    payment_id: UUID
    idempotency_key: UUID
    amount: Decimal
    currency: str
    description: str
    webhook_url: str
    status: str
    created_at: datetime
    processed_at: datetime | None
    metadata: dict[str, Any]
