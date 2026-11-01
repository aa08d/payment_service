import asyncio
import logging
import signal
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import make_async_container
from faststream.rabbit import RabbitBroker

from payment.bootstrap.config import AppConfig, load_app_config
from payment.bootstrap.di import get_providers
from payment.infrastructure.message_broker.topology import declare_topology
from payment.infrastructure.outbox import OutboxRelay, run_relay_loop

logger = logging.getLogger(__name__)


async def run_relay(config: AppConfig, stop_event: asyncio.Event) -> None:
    broker = RabbitBroker(config.rabbit.url)
    container = make_async_container(*get_providers(), context={AppConfig: config, RabbitBroker: broker})

    @asynccontextmanager
    async def relay_scope() -> AsyncIterator[OutboxRelay]:
        async with container() as request_container:
            yield await request_container.get(OutboxRelay)

    await broker.connect()
    await declare_topology(broker, config.consumer)
    await broker.start()
    logger.info("Outbox relay started")

    try:
        await run_relay_loop(relay_scope, config.outbox, stop_event)
    finally:
        await broker.stop()
        await container.close()
        logger.info("Outbox relay stopped")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await run_relay(load_app_config(), stop_event)


if __name__ == "__main__":
    asyncio.run(main())
