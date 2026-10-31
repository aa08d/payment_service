import copy
from typing import Any, Self

from payment.domain.common.entities import AggregateRoot
from payment.domain.payment.events import (
    PaymentCreated,
    PaymentFailed,
    PaymentSucceeded,
)
from payment.domain.payment.value_objects import (
    Description,
    IdempotencyKey,
    Money,
    PaymentID,
    PaymentStatus,
    PaymentTimestamps,
    WebhookURL,
)


class Payment(AggregateRoot):
    def __init__(
        self,
        payment_id: PaymentID,
        idempotency_key: IdempotencyKey,
        money: Money,
        description: Description,
        webhook_url: WebhookURL,
        status: PaymentStatus,
        timestamps: PaymentTimestamps,
        metadata: dict[str, Any],
    ) -> None:
        self.payment_id = payment_id
        self.idempotency_key = idempotency_key
        self.money = money
        self.description = description
        self.webhook_url = webhook_url
        self.status = status
        self.timestamps = timestamps
        self.metadata = copy.deepcopy(metadata)

    @classmethod
    def create(
        cls,
        idempotency_key: IdempotencyKey,
        money: Money,
        description: Description,
        webhook_url: WebhookURL,
        metadata: dict[str, Any],
    ) -> Self:
        payment_id = PaymentID.create()
        status = PaymentStatus.create()
        timestamps = PaymentTimestamps.create()

        payment = cls(
            payment_id=payment_id,
            idempotency_key=idempotency_key,
            money=money,
            description=description,
            webhook_url=webhook_url,
            status=status,
            timestamps=timestamps,
            metadata=metadata,
        )

        payment.record_event(
            PaymentCreated(
                payment_id=payment.payment_id.value,
                idempotency_key=payment.idempotency_key.value,
                amount=payment.money.amount,
                currency=payment.money.currency.value,
                description=payment.description.value,
                webhook_url=payment.webhook_url.value,
                status=payment.status.value,
                metadata=copy.deepcopy(payment.metadata),
            )
        )

        return payment

    def succeed(self) -> None:
        self.status = self.status.succeed()
        self.timestamps = self.timestamps.mark_processed()

        self.record_event(
            PaymentSucceeded(
                payment_id=self.payment_id.value,
                idempotency_key=self.idempotency_key.value,
                amount=self.money.amount,
                currency=self.money.currency.value,
                webhook_url=self.webhook_url.value,
                status=self.status.value,
                processed_at=self.timestamps.processed_at,
                metadata=copy.deepcopy(self.metadata),
            )
        )

    def fail(self) -> None:
        self.status = self.status.fail()
        self.timestamps = self.timestamps.mark_processed()

        self.record_event(
            PaymentFailed(
                payment_id=self.payment_id.value,
                idempotency_key=self.idempotency_key.value,
                amount=self.money.amount,
                currency=self.money.currency.value,
                webhook_url=self.webhook_url.value,
                status=self.status.value,
                processed_at=self.timestamps.processed_at,
                metadata=copy.deepcopy(self.metadata),
            )
        )
