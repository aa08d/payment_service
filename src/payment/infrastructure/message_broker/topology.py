from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit.schemas.queue import ClassicQueueArgs

from payment.domain.common.events import Event
from payment.domain.payment.events import PaymentCreated, PaymentFailed, PaymentSucceeded

from .config import ConsumerConfig

PAYMENTS_EXCHANGE = "payments"
DEAD_LETTER_EXCHANGE = "payments.dlx"

NEW_PAYMENTS_QUEUE = "payments.new"
WEBHOOK_QUEUE = "payments.webhook"

WORK_QUEUES = (NEW_PAYMENTS_QUEUE, WEBHOOK_QUEUE)

ROUTING_KEYS: dict[type[Event], str] = {
    PaymentCreated: NEW_PAYMENTS_QUEUE,
    PaymentSucceeded: WEBHOOK_QUEUE,
    PaymentFailed: WEBHOOK_QUEUE,
}

ATTEMPT_HEADER = "x-attempt"
ERROR_HEADER = "x-error"

DEFAULT_EXCHANGE = ""


def retry_queue_name(queue: str, retry_number: int) -> str:
    return f"{queue}.retry.{retry_number}"


def dead_letter_queue_name(queue: str) -> str:
    return f"{queue}.dlq"


def retry_delay_seconds(retry_number: int, base_delay_seconds: float) -> float:
    return base_delay_seconds * float(2 ** (retry_number - 1))


async def declare_topology(broker: RabbitBroker, config: ConsumerConfig) -> None:
    payments = RabbitExchange(PAYMENTS_EXCHANGE)
    dead_letters = RabbitExchange(DEAD_LETTER_EXCHANGE)
    await broker.declare_exchange(payments)
    await broker.declare_exchange(dead_letters)

    for queue in WORK_QUEUES:
        dlq = dead_letter_queue_name(queue)

        await _declare_queue(broker, dlq, bind_to=dead_letters)

        work_queue_arguments: ClassicQueueArgs = {
            "x-dead-letter-exchange": DEAD_LETTER_EXCHANGE,
            "x-dead-letter-routing-key": dlq,
        }

        await _declare_queue(
            broker,
            queue,
            bind_to=payments,
            arguments=work_queue_arguments,
        )

        for retry_number in range(1, config.max_attempts):
            delay_seconds = retry_delay_seconds(
                retry_number,
                config.retry_base_delay_seconds,
            )

            retry_queue_arguments: ClassicQueueArgs = {
                "x-message-ttl": int(delay_seconds * 1000),
                "x-dead-letter-exchange": DEFAULT_EXCHANGE,
                "x-dead-letter-routing-key": queue,
            }

            await _declare_queue(
                broker,
                retry_queue_name(queue, retry_number),
                arguments=retry_queue_arguments,
            )


async def _declare_queue(
    broker: RabbitBroker,
    name: str,
    *,
    arguments: ClassicQueueArgs | None = None,
    bind_to: RabbitExchange | None = None,
) -> None:
    queue = await broker.declare_queue(RabbitQueue(name, durable=True, arguments=arguments))
    if bind_to is not None:
        exchange = await broker.declare_exchange(bind_to)
        await queue.bind(exchange, routing_key=name)
