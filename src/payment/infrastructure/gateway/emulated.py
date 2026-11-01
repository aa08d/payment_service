import asyncio
import random
from decimal import Decimal
from uuid import UUID

from payment.application.payment.interfaces import PaymentGateway
from payment.application.payment.interfaces.gateway import GatewayResult

from .config import GatewayConfig


class EmulatedPaymentGateway(PaymentGateway):
    def __init__(self, config: GatewayConfig) -> None:
        self._config = config

    async def process(self, payment_id: UUID, amount: Decimal, currency: str) -> GatewayResult:
        await asyncio.sleep(random.uniform(self._config.min_delay_seconds, self._config.max_delay_seconds))

        if random.Random(payment_id.int).random() < self._config.success_rate:
            return GatewayResult.approve()

        return GatewayResult.decline()
