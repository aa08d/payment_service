from adaptix import Retort

from payment.domain.common.events import Event
from payment.infrastructure.message_broker.topology import ROUTING_KEYS

from .message import OutboxMessage


class OutboxMessageMapper:
    def __init__(self, routing_keys: dict[type[Event], str] | None = None) -> None:
        self._routing_keys = ROUTING_KEYS if routing_keys is None else routing_keys
        self._retort = Retort()

    def to_message(self, event: Event) -> OutboxMessage:
        event_type = type(event)
        routing_key = self._routing_keys.get(event_type)

        if routing_key is None:
            raise ValueError(f"Routing key is not configured for event type: {event_type.__name__}")

        return OutboxMessage(
            id=event.event_id,
            event_type=event_type.__name__,
            routing_key=routing_key,
            payload=self._retort.dump(event, event_type),
            created_at=event.event_timestamp,
        )
