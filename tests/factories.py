from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from payment.application.payment.commands import CreatePaymentCommand
from payment.application.payment.dto import PaymentDetailDTO
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
    """Return a pending payment as if it was just loaded from the storage (without recorded events)."""
    payment = Payment.create(
        idempotency_key=IdempotencyKey(idempotency_key),
        money=Money(amount, currency),
        description=Description(description),
        webhook_url=WebhookURL(webhook_url),
        metadata={"order_id": 123} if metadata is None else metadata,
    )
    payment.clear_events()
    return payment


def create_payment_command(**changes: Any) -> CreatePaymentCommand:
    command = CreatePaymentCommand(
        idempotency_key=IDEMPOTENCY_KEY,
        amount=Decimal("1500.00"),
        currency=Currency.RUB,
        description="Order #123",
        webhook_url="https://example.com/webhook",
        metadata={"order_id": 123},
    )
    return replace(command, **changes)


def create_payment_detail(**changes: Any) -> PaymentDetailDTO:
    payment = PaymentDetailDTO(
        payment_id=PAYMENT_ID,
        idempotency_key=IDEMPOTENCY_KEY,
        amount=Decimal("1500.00"),
        currency="RUB",
        description="Order #123",
        webhook_url="https://example.com/webhook",
        status="succeeded",
        created_at=datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC),
        processed_at=datetime(2026, 10, 31, 12, 0, 3, tzinfo=UTC),
        metadata={"order_id": 123},
    )
    return replace(payment, **changes)
