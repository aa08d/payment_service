from abc import ABC, abstractmethod
from typing import Any

from .command import Command


class CommandHandler[C: Command[Any], R](ABC):
    @abstractmethod
    async def __call__(self, command: C) -> R:
        raise NotImplementedError
