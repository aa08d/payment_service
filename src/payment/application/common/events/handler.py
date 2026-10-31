from abc import ABC, abstractmethod

from payment.domain.common.events import Event


class EventHandler[E: Event](ABC):
    @abstractmethod
    async def __call__(self, event: E) -> None:
        raise NotImplementedError
