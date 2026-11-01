from collections.abc import Sequence

from payment.application.common.commands import Command
from payment.application.common.mediator import Mediator
from payment.application.common.queries import Query
from payment.domain.common.events import Event


class MediatorMock(Mediator):
    def __init__(self) -> None:
        self.published_events: list[Event] = []

    async def send[R](self, request: Command[R] | Query[R]) -> R:
        raise NotImplementedError

    async def publish(self, events: Event | Sequence[Event]) -> None:
        if isinstance(events, Event):
            events = [events]
        self.published_events.extend(events)
