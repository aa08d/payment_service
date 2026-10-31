from abc import ABC, abstractmethod
from typing import Any

from .query import Query


class QueryHandler[Q: Query[Any], R](ABC):
    @abstractmethod
    async def __call__(self, query: Q) -> R:
        raise NotImplementedError
