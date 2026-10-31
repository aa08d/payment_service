from collections.abc import Awaitable, Callable, Sequence

from dishka import AsyncContainer

from payment.application.common.commands import Command
from payment.application.common.mediator import Mediator, MediatorRegistry
from payment.application.common.queries import Query
from payment.domain.common.events import Event


class DishkaMediator(Mediator):
    def __init__(self, registry: MediatorRegistry, container: AsyncContainer) -> None:
        self._registry = registry
        self._container = container

    async def send[R](self, request: Command[R] | Query[R]) -> R:
        handler_type = self._registry.get_request_handler(type(request))
        handler: Callable[[Command[R] | Query[R]], Awaitable[R]] = await self._container.get(handler_type)
        return await handler(request)

    async def publish(self, events: Event | Sequence[Event]) -> None:
        if isinstance(events, Event):
            events = [events]

        for event in events:
            for handler_type in self._registry.get_event_handlers(type(event)):
                handler = await self._container.get(handler_type)
                await handler(event)
