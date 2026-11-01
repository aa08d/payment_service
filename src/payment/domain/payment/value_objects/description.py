from dataclasses import dataclass

from payment.domain.common.exceptions import DomainError
from payment.domain.common.value_objects import ValueObject

MAX_DESCRIPTION_LENGTH = 250


class DescriptionError(DomainError):
    pass


class TooLongDescriptionError(DescriptionError):
    def __init__(self, description: str) -> None:
        self._description = description

    @property
    def message(self) -> str:
        return f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters; got {len(self._description)}"


@dataclass(frozen=True)
class Description(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > MAX_DESCRIPTION_LENGTH:
            raise TooLongDescriptionError(self.value)
