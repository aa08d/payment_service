import asyncio
import logging
from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager

from dishka import make_async_container
from faststream import AckPolicy, FastStream
from faststream.rabbit import Channel, RabbitBroker, RabbitQueue

from payment.bootstrap.config import AppConfig, load_app_config
from payment.bootstrap.di import get_providers
from payment.infrastructure.message_broker.config import ConsumerConfig
from payment.infrastructure.message_broker.retry import MessageRetrier
from payment.infrastructure.message_broker.topology import declare_topology
from payment.presentation.consumer import PaymentConsumer, ProcessPaymentConsumer, SendWebhookConsumer


def register_consumers(broker: RabbitBroker, consumers: Iterable[PaymentConsumer], config: ConsumerConfig) -> None:
    for consumer in consumers:
        broker.subscriber(
            RabbitQueue(consumer.queue, declare=False),
            channel=Channel(prefetch_count=config.prefetch_count),
            ack_policy=AckPolicy.REJECT_ON_ERROR,
        )(consumer.handle)


def create_app(config: AppConfig | None = None) -> FastStream:
    config = config or load_app_config()

    broker = RabbitBroker(config.rabbit.url)
    container = make_async_container(*get_providers(), context={AppConfig: config, RabbitBroker: broker})
    retrier = MessageRetrier(broker, config.consumer)

    register_consumers(
        broker,
        (ProcessPaymentConsumer(container, retrier), SendWebhookConsumer(container, retrier)),
        config.consumer,
    )

    @asynccontextmanager
    async def lifespan() -> AsyncIterator[None]:
        await broker.connect()
        await declare_topology(broker, config.consumer)
        try:
            yield
        finally:
            await container.close()

    return FastStream(broker, lifespan=lifespan)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(create_app().run())


if __name__ == "__main__":
    main()
