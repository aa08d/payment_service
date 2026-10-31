from typing import Protocol
from uuid import UUID

from payment.infrastructure.outbox.message import OutboxMessage


class OutboxRepository(Protocol):
    async def add(self, message: OutboxMessage) -> None:
        raise NotImplementedError

    async def fetch_unpublished(self, limit: int) -> list[OutboxMessage]:
        raise NotImplementedError

    async def mark_published(self, ids: list[UUID]) -> None:
        raise NotImplementedError
