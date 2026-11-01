from faststream.rabbit import RabbitBroker, RabbitExchange

from payment.infrastructure.message_broker.topology import PAYMENTS_EXCHANGE

from .interfaces import MessagePublisher
from .message import OutboxMessage


class RabbitMessagePublisher(MessagePublisher):
    def __init__(self, broker: RabbitBroker) -> None:
        self._broker = broker
        self._exchange = RabbitExchange(PAYMENTS_EXCHANGE, declare=False)

    async def publish(self, message: OutboxMessage) -> None:
        await self._broker.publish(
            message.payload,
            exchange=self._exchange,
            routing_key=message.routing_key,
            message_id=str(message.id),
            message_type=message.event_type,
            persist=True,
        )
