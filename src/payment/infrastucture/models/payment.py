from sqlalchemy import UUID, Column, DateTime, Enum, Numeric, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import composite

from payment.domain.payment.entities import Payment
from payment.domain.payment.value_objects import (
    Currency,
    Description,
    IdempotencyKey,
    Money,
    PaymentID,
    PaymentStatus,
    PaymentTimestamps,
    WebhookURL,
)

from .base import BaseModel, mapper_registry

PAYMENT_TABLE = Table(
    "payments",
    BaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("idempotency_key", UUID(as_uuid=True), nullable=False, unique=True),
    Column("amount", Numeric(18, 2), nullable=False),
    Column("currency", Enum(Currency, name="currency"), nullable=False),
    Column("description", String(250), nullable=False),
    Column("webhook_url", String, nullable=False),
    Column("status", Enum(PaymentStatus, name="payment_status"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("processed_at", DateTime(timezone=True), nullable=True),
    Column("metadata", JSONB, nullable=False),
)

mapper_registry.map_imperatively(
    Payment,
    PAYMENT_TABLE,
    properties={
        "_idempotency_key": PAYMENT_TABLE.c.idempotency_key,
        "_description": PAYMENT_TABLE.c.description,
        "_webhook_url": PAYMENT_TABLE.c.webhook_url,
        "payment_id": composite(PaymentID, PAYMENT_TABLE.c.id),
        "idempotency_key": composite(IdempotencyKey, "_idempotency_key"),
        "money": composite(Money, PAYMENT_TABLE.c.amount, PAYMENT_TABLE.c.currency),
        "description": composite(Description, "_description"),
        "webhook_url": composite(WebhookURL, "_webhook_url"),
        "status": PAYMENT_TABLE.c.status,
        "timestamps": composite(PaymentTimestamps, PAYMENT_TABLE.c.created_at, PAYMENT_TABLE.c.processed_at),
        "metadata": PAYMENT_TABLE.c.metadata,
    },
)
