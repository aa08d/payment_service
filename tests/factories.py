from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.domain.payment.entities import Payment
from payment.domain.payment.value_objects import Currency, Description, IdempotencyKey, Money, WebhookURL

PAYMENT_ID = UUID("123e4567-e89b-12d3-a456-426614174000")
IDEMPOTENCY_KEY = UUID("123e4567-e89b-12d3-a456-426614174001")


def create_payment(
    *,
    idempotency_key: UUID = IDEMPOTENCY_KEY,
    amount: Decimal = Decimal("1500.00"),
    currency: Currency = Currency.RUB,
    description: str = "Order #123",
    webhook_url: str = "https://example.com/webhook",
    metadata: dict[str, Any] | None = None,
) -> Payment:
    payment = Payment.create(
        idempotency_key=IdempotencyKey(idempotency_key),
        money=Money(amount, currency),
        description=Description(description),
        webhook_url=WebhookURL(webhook_url),
        metadata={"order_id": 123} if metadata is None else metadata,
    )
    payment.clear_events()
    return payment
