from dataclasses import dataclass
from uuid import UUID

from payment.domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class IdempotencyKey(ValueObject):
    value: UUID
