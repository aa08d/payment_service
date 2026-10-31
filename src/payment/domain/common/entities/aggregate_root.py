from abc import ABC

from payment.domain.common.events import Event


class AggregateRoot(ABC):
    def record_event(self, event: Event) -> None:
        self._ensure_events().append(event)

    def clear_events(self) -> None:
        self._ensure_events().clear()

    def pull_events(self) -> list[Event]:
        events = self._ensure_events().copy()
        self.clear_events()
        return events

    def _ensure_events(self) -> list[Event]:
        if not hasattr(self, "_events"):
            self._events: list[Event] = []

        return self._events
