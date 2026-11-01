from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid7

from payment.domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class PaymentID(ValueObject):
    value: UUID

    @classmethod
    def create(cls) -> Self:
        return cls(uuid7())
