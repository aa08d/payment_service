import logging

from payment.application.common.interfaces import UnitOfWork

from .interfaces import MessagePublisher, OutboxRepository

logger = logging.getLogger(__name__)


class OutboxRelay:
    def __init__(
        self,
        repository: OutboxRepository,
        publisher: MessagePublisher,
        uow: UnitOfWork,
        batch_size: int,
    ) -> None:
        self._repository = repository
        self._publisher = publisher
        self._uow = uow
        self._batch_size = batch_size

    async def run_once(self) -> int:
        messages = await self._repository.fetch_unpublished(self._batch_size)

        published_ids = []
        error: Exception | None = None

        for message in messages:
            try:
                await self._publisher.publish(message)
            except Exception as err:
                logger.exception("Failed to publish outbox message", extra={"outbox_id": message.id})
                error = err
                break

            published_ids.append(message.id)

        if published_ids:
            await self._repository.mark_published(published_ids)
            await self._uow.commit()

        if error is not None:
            raise error

        return len(published_ids)
