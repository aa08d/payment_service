import logging

from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitMessage, RabbitQueue

from .config import ConsumerConfig
from .topology import (
    ATTEMPT_HEADER,
    DEAD_LETTER_EXCHANGE,
    ERROR_HEADER,
    dead_letter_queue_name,
    retry_delay_seconds,
    retry_queue_name,
)

logger = logging.getLogger(__name__)

ERROR_MAX_LENGTH = 1000


class MessageRetrier:
    def __init__(self, broker: RabbitBroker, config: ConsumerConfig) -> None:
        self._broker = broker
        self._config = config
        self._dead_letter_exchange = RabbitExchange(DEAD_LETTER_EXCHANGE, declare=False)

    @staticmethod
    def attempt_of(message: RabbitMessage) -> int:
        return int(message.headers.get(ATTEMPT_HEADER, 1))

    async def retry_or_dead_letter(self, queue: str, message: RabbitMessage, attempt: int, error: Exception) -> None:
        if attempt >= self._config.max_attempts:
            await self._dead_letter(queue, message, attempt, error)
        else:
            await self._retry(queue, message, attempt, error)

    async def _dead_letter(self, queue: str, message: RabbitMessage, attempt: int, error: Exception) -> None:
        logger.error(
            "Attempts exhausted, moving message to DLQ",
            extra={"queue": queue, "message_id": message.message_id, "attempts": attempt},
        )
        await self._republish(
            message,
            attempt=attempt,
            error=error,
            exchange=self._dead_letter_exchange,
            routing_key=dead_letter_queue_name(queue),
        )

    async def _retry(self, queue: str, message: RabbitMessage, attempt: int, error: Exception) -> None:
        delay = retry_delay_seconds(attempt, self._config.retry_base_delay_seconds)
        logger.info(
            "Scheduling retry",
            extra={
                "queue": queue,
                "message_id": message.message_id,
                "next_attempt": attempt + 1,
                "delay_seconds": delay,
            },
        )
        await self._republish(
            message,
            attempt=attempt + 1,
            error=error,
            queue=RabbitQueue(retry_queue_name(queue, attempt), declare=False),
        )

    async def _republish(
        self,
        message: RabbitMessage,
        *,
        attempt: int,
        error: Exception,
        queue: RabbitQueue | None = None,
        exchange: RabbitExchange | None = None,
        routing_key: str = "",
    ) -> None:
        await self._broker.publish(
            message.body,
            queue=queue or "",
            exchange=exchange,
            routing_key=routing_key,
            headers={ATTEMPT_HEADER: attempt, ERROR_HEADER: repr(error)[:ERROR_MAX_LENGTH]},
            message_id=message.message_id,
            content_type=message.content_type,
            persist=True,
        )
