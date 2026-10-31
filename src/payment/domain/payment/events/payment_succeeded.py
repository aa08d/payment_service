from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.domain.common.events import Event


@dataclass(frozen=True)
class PaymentSucceeded(Event):
    payment_id: UUID
    idempotency_key: UUID
    amount: Decimal
    currency: str
    webhook_url: str
    status: str
    processed_at: datetime
    metadata: dict[str, Any]
