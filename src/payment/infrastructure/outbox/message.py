from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    event_type: str
    routing_key: str | None
    payload: dict[str, Any]
    created_at: datetime
