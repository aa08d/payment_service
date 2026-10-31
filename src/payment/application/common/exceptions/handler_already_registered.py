from typing import Any

from payment.application.common.commands import Command
from payment.application.common.queries import Query

from .application import ApplicationError


class HandlerAlreadyRegisteredError(ApplicationError):
    def __init__(self, request: type[Command[Any]] | type[Query[Any]]) -> None:
        self._request = request

    @property
    def message(self) -> str:
        return f"Handler for {self._request.__name__} is already registered"
