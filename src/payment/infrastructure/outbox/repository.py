from uuid import UUID

from sqlalchemy import func, insert, select, update

from payment.infrastructure.database.models.outbox import OUTBOX_TABLE
from payment.infrastructure.database.repositories.base import SQLAlchemyRepository

from .interfaces import OutboxRepository
from .message import OutboxMessage


class OutboxSQLAlchemyRepository(SQLAlchemyRepository, OutboxRepository):
    async def add(self, message: OutboxMessage) -> None:
        await self._session.execute(
            insert(OUTBOX_TABLE).values(
                id=message.id,
                event_type=message.event_type,
                routing_key=message.routing_key,
                payload=message.payload,
                created_at=message.created_at,
            )
        )

    async def fetch_unpublished(self, limit: int) -> list[OutboxMessage]:
        result = await self._session.execute(
            select(OUTBOX_TABLE)
            .where(OUTBOX_TABLE.c.published_at.is_(None))
            .order_by(OUTBOX_TABLE.c.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        return [
            OutboxMessage(
                id=row["id"],
                event_type=row["event_type"],
                routing_key=row["routing_key"],
                payload=row["payload"],
                created_at=row["created_at"],
            )
            for row in result.mappings()
        ]

    async def mark_published(self, ids: list[UUID]) -> None:
        await self._session.execute(
            update(OUTBOX_TABLE).where(OUTBOX_TABLE.c.id.in_(ids)).values(published_at=func.now())
        )
