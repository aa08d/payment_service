from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.domain.common.events import Event


@dataclass(frozen=True)
class PaymentCreated(Event):
    payment_id: UUID
    idempotency_key: UUID
    amount: Decimal
    currency: str
    description: str
    webhook_url: str
    status: str
    metadata: dict[str, Any]
