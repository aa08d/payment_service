from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, Self
from uuid import UUID

from payment.application.common.dto import DTO


@dataclass(frozen=True)
class GatewayResult(DTO):
    approved: bool

    @classmethod
    def approve(cls) -> Self:
        return cls(approved=True)

    @classmethod
    def decline(cls) -> Self:
        return cls(approved=False)


class PaymentGateway(Protocol):
    async def process(self, payment_id: UUID, amount: Decimal, currency: str) -> GatewayResult:
        raise NotImplementedError
