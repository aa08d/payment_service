from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from payment.domain.payment.value_objects import Currency, PaymentStatus


class CreatePaymentRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": "1500.00",
                "currency": "RUB",
                "description": "Заказ №123",
                "metadata": {"order_id": 123},
                "webhook_url": "https://webhook.site/your-id",
            }
        }
    )

    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: Currency
    description: str = Field(max_length=250)
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class CreatePaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    payment_id: UUID
    idempotency_key: UUID
    amount: Decimal
    currency: Currency
    description: str
    webhook_url: str
    status: PaymentStatus
    created_at: datetime
    processed_at: datetime | None
    metadata: dict[str, Any]


class ErrorResponse(BaseModel):
    code: str
    detail: str
