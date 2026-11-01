from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from payment.application.payment.interfaces import PaymentGateway
from payment.application.payment.interfaces.gateway import GatewayResult


@dataclass(frozen=True)
class GatewayCall:
    payment_id: UUID
    amount: Decimal
    currency: str


class PaymentGatewayMock(PaymentGateway):
    def __init__(self) -> None:
        self.result = GatewayResult.approve()
        self.error: Exception | None = None
        self.calls: list[GatewayCall] = []

    async def process(self, payment_id: UUID, amount: Decimal, currency: str) -> GatewayResult:
        self.calls.append(GatewayCall(payment_id=payment_id, amount=amount, currency=currency))
        if self.error is not None:
            raise self.error
        return self.result
