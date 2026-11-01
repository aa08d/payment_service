from typing import Protocol

from payment.infrastructure.outbox.message import OutboxMessage


class MessagePublisher(Protocol):
    async def publish(self, message: OutboxMessage) -> None:
        raise NotImplementedError
