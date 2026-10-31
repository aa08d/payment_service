from dataclasses import dataclass

import pytest

from payment.application.common.commands import Command, CommandHandler
from payment.application.common.events import EventHandler
from payment.application.common.exceptions import HandlerAlreadyRegisteredError, HandlerNotRegisteredError
from payment.application.common.mediator import MediatorRegistry
from payment.domain.common.events import Event


@dataclass(frozen=True)
class SomeCommand(Command[None]):
    pass


@dataclass(frozen=True)
class OtherCommand(Command[None]):
    pass


class SomeCommandHandler(CommandHandler[SomeCommand, None]):
    async def __call__(self, command: SomeCommand) -> None:
        pass


@dataclass(frozen=True)
class BaseEvent(Event):
    pass


@dataclass(frozen=True)
class ChildEvent(BaseEvent):
    pass


class FirstEventHandler(EventHandler[ChildEvent]):
    async def __call__(self, event: ChildEvent) -> None:
        pass


class SecondEventHandler(EventHandler[ChildEvent]):
    async def __call__(self, event: ChildEvent) -> None:
        pass


class BaseEventHandler(EventHandler[BaseEvent]):
    async def __call__(self, event: BaseEvent) -> None:
        pass


def test_registry_returns_registered_request_handler() -> None:
    registry = MediatorRegistry()
    registry.register_request(SomeCommand, SomeCommandHandler)

    assert registry.get_request_handler(SomeCommand) is SomeCommandHandler


def test_registry_request_handler_cannot_be_registered_twice() -> None:
    registry = MediatorRegistry()
    registry.register_request(SomeCommand, SomeCommandHandler)

    with pytest.raises(HandlerAlreadyRegisteredError):
        registry.register_request(SomeCommand, SomeCommandHandler)


def test_registry_unknown_request_has_no_handler() -> None:
    registry = MediatorRegistry()
    registry.register_request(SomeCommand, SomeCommandHandler)

    with pytest.raises(HandlerNotRegisteredError):
        registry.get_request_handler(OtherCommand)


def test_registry_event_can_have_several_handlers_in_registration_order() -> None:
    registry = MediatorRegistry()
    registry.register_event(ChildEvent, FirstEventHandler)
    registry.register_event(ChildEvent, SecondEventHandler)

    assert registry.get_event_handlers(ChildEvent) == [FirstEventHandler, SecondEventHandler]


def test_registry_event_without_handlers() -> None:
    registry = MediatorRegistry()
    registry.register_event(ChildEvent, FirstEventHandler)

    assert registry.get_event_handlers(BaseEvent) == []


def test_registry_event_handlers_of_parent_event_are_inherited() -> None:
    registry = MediatorRegistry()
    registry.register_event(BaseEvent, BaseEventHandler)
    registry.register_event(ChildEvent, FirstEventHandler)

    assert registry.get_event_handlers(ChildEvent) == [FirstEventHandler, BaseEventHandler]
