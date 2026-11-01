from payment.application.common.events import EventHandler
from payment.domain.common.events import Event
from payment.infrastructure.outbox.interfaces import OutboxRepository

from .mapper import OutboxMessageMapper


class OutboxEventHandler(EventHandler[Event]):
    def __init__(self, mapper: OutboxMessageMapper, repository: OutboxRepository) -> None:
        self._mapper = mapper
        self._repository = repository

    async def __call__(self, event: Event) -> None:
        await self._repository.add(self._mapper.to_message(event))
