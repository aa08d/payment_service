from typing import Protocol

from payment.application.common.commands import Command
from payment.application.common.queries import Query
from payment.domain.common.events import Event


class Mediator(Protocol):
    async def send[R](self, request: Command[R] | Query[R]) -> R:
        raise NotImplementedError

    async def publish(self, events: Event | list[Event]) -> None:
        raise NotImplementedError
