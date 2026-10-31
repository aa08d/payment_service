from inspect import getmro
from typing import Any

from payment.application.common.commands import Command, CommandHandler
from payment.application.common.events import EventHandler
from payment.application.common.exceptions import HandlerAlreadyRegisteredError, HandlerNotRegisteredError
from payment.application.common.queries import Query, QueryHandler
from payment.domain.common.events import Event


class MediatorRegistry:
    def __init__(self) -> None:
        self._requests: dict[type, type] = {}
        self._events: dict[type, list[type[EventHandler[Any]]]] = {}

    def register_request(
        self,
        request: type[Command[Any]] | type[Query[Any]],
        handler: type[CommandHandler[Any, Any]] | type[QueryHandler[Any, Any]],
    ) -> None:
        if request in self._requests:
            raise HandlerAlreadyRegisteredError(request)

        self._requests[request] = handler

    def register_event(self, event: type[Event], handler: type[EventHandler[Any]]) -> None:
        self._events.setdefault(event, []).append(handler)

    def get_request_handler(self, request: type[Command[Any]] | type[Query[Any]]) -> type:
        if (handler := self._requests.get(request)) is None:
            raise HandlerNotRegisteredError(request)

        return handler

    def get_event_handlers(self, event: type[Event]) -> list[type[EventHandler[Any]]]:
        handlers: list[type[EventHandler[Any]]] = []

        for event_type in getmro(event):
            handlers.extend(self._events.get(event_type, ()))

        return handlers
