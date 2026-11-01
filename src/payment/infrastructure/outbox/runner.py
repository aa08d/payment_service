import asyncio
import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager, suppress

from .config import OutboxConfig
from .relay import OutboxRelay

logger = logging.getLogger(__name__)

ERROR_BACKOFF_SECONDS = 5.0

RelayScope = Callable[[], AbstractAsyncContextManager[OutboxRelay]]


async def run_relay_loop(
    relay_scope: RelayScope,
    config: OutboxConfig,
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        delay = await _run_iteration(relay_scope, config)
        await _sleep_unless_stopped(stop_event, delay)


async def _run_iteration(relay_scope: RelayScope, config: OutboxConfig) -> float:
    try:
        async with relay_scope() as relay:
            published = await relay.run_once()
    except Exception:
        logger.exception("Outbox relay iteration failed")
        return ERROR_BACKOFF_SECONDS

    if not published:
        return config.poll_interval_seconds

    logger.info("Outbox messages published", extra={"count": published})
    return 0 if published >= config.batch_size else config.poll_interval_seconds


async def _sleep_unless_stopped(stop_event: asyncio.Event, delay: float) -> None:
    if delay <= 0:
        return
    with suppress(TimeoutError):
        await asyncio.wait_for(stop_event.wait(), timeout=delay)
