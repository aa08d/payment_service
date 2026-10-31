from sqlalchemy import UUID, Column, DateTime, Index, String, Table, text
from sqlalchemy.dialects.postgresql import JSONB

from .base import BaseModel

OUTBOX_TABLE = Table(
    "outbox",
    BaseModel.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("event_type", String, nullable=False),
    Column("routing_key", String, nullable=False),
    Column("payload", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("published_at", DateTime(timezone=True), nullable=True),
    Index(
        "ix_outbox_unpublished_created_at",
        "created_at",
        postgresql_where=text("published_at IS NULL"),
    ),
)
