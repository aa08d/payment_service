from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from payment.domain.payment.entities import Payment
from payment.domain.payment.events import PaymentCreated, PaymentFailed, PaymentSucceeded
from payment.domain.payment.value_objects import (
    Currency,
    Description,
    IdempotencyKey,
    Money,
    PaymentID,
    PaymentStatus,
    PaymentTimestamps,
    WebhookURL,
)
from payment.domain.payment.value_objects.payment_status import InvalidStatusTransitionError
from tests.factories import IDEMPOTENCY_KEY, create_payment


def make_payment(metadata: dict[str, object] | None = None) -> Payment:
    return Payment.create(
        idempotency_key=IdempotencyKey(IDEMPOTENCY_KEY),
        money=Money(Decimal("1500.00"), Currency.RUB),
        description=Description("Order #123"),
        webhook_url=WebhookURL("https://example.com/webhook"),
        metadata={"order_id": 123} if metadata is None else metadata,
    )


def test_new_payment_is_pending_and_not_processed() -> None:
    payment = make_payment()

    assert payment.status is PaymentStatus.pending
    assert payment.timestamps.created_at.tzinfo is UTC
    assert payment.timestamps.processed_at is None


def test_new_payment_keeps_passed_data() -> None:
    payment = make_payment()

    assert payment.idempotency_key == IdempotencyKey(IDEMPOTENCY_KEY)
    assert payment.money == Money(Decimal("1500.00"), Currency.RUB)
    assert payment.description == Description("Order #123")
    assert payment.webhook_url == WebhookURL("https://example.com/webhook")
    assert payment.metadata == {"order_id": 123}


def test_new_payments_get_different_ids() -> None:
    assert make_payment().payment_id != make_payment().payment_id


def test_new_payment_records_payment_created_event() -> None:
    payment = make_payment()

    events = payment.pull_events()

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, PaymentCreated)
    assert event.payment_id == payment.payment_id.value
    assert event.idempotency_key == IDEMPOTENCY_KEY
    assert event.amount == Decimal("1500.00")
    assert event.currency == "RUB"
    assert event.description == "Order #123"
    assert event.webhook_url == "https://example.com/webhook"
    assert event.status == "pending"
    assert event.metadata == {"order_id": 123}


def test_new_payment_copies_metadata() -> None:
    metadata = {"order": {"id": 123}}
    payment = make_payment(metadata)

    metadata["order"]["id"] = 124  # type: ignore[index]
    metadata["extra"] = True

    assert payment.metadata == {"order": {"id": 123}}


def test_payment_created_event_has_its_own_copy_of_metadata() -> None:
    payment = make_payment({"order": {"id": 123}})

    payment.metadata["order"]["id"] = 124  # type: ignore[index]
    event = payment.pull_events()[0]

    assert isinstance(event, PaymentCreated)
    assert event.metadata == {"order": {"id": 123}}


def test_succeed_changes_status_marks_processing_time_and_records_event() -> None:
    payment = make_payment()
    payment.clear_events()

    payment.succeed()

    assert payment.status is PaymentStatus.succeeded
    assert payment.timestamps.processed_at is not None
    assert payment.timestamps.processed_at >= payment.timestamps.created_at

    events = payment.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, PaymentSucceeded)
    assert event.payment_id == payment.payment_id.value
    assert event.idempotency_key == IDEMPOTENCY_KEY
    assert event.amount == Decimal("1500.00")
    assert event.currency == "RUB"
    assert event.webhook_url == "https://example.com/webhook"
    assert event.status == "succeeded"
    assert event.processed_at == payment.timestamps.processed_at
    assert event.metadata == {"order_id": 123}


def test_fail_changes_status_marks_processing_time_and_records_event() -> None:
    payment = make_payment()
    payment.clear_events()

    payment.fail()

    assert payment.status is PaymentStatus.failed
    assert payment.timestamps.processed_at is not None
    assert payment.timestamps.processed_at >= payment.timestamps.created_at

    events = payment.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, PaymentFailed)
    assert event.payment_id == payment.payment_id.value
    assert event.status == "failed"
    assert event.processed_at == payment.timestamps.processed_at
    assert event.metadata == {"order_id": 123}


def test_processing_does_not_change_payment_data() -> None:
    payment = make_payment()
    payment_id = payment.payment_id
    created_at = payment.timestamps.created_at

    payment.succeed()

    assert payment.payment_id == payment_id
    assert payment.timestamps.created_at == created_at
    assert payment.money == Money(Decimal("1500.00"), Currency.RUB)
    assert payment.description == Description("Order #123")
    assert payment.webhook_url == WebhookURL("https://example.com/webhook")
    assert payment.metadata == {"order_id": 123}


@pytest.mark.parametrize(
    ("first", "second", "target"),
    [
        ("succeed", "succeed", "succeeded"),
        ("succeed", "fail", "failed"),
        ("fail", "succeed", "succeeded"),
        ("fail", "fail", "failed"),
    ],
)
def test_processed_payment_cannot_be_processed_again(first: str, second: str, target: str) -> None:
    payment = create_payment()
    getattr(payment, first)()
    payment.clear_events()
    status = payment.status
    processed_at = payment.timestamps.processed_at

    with pytest.raises(InvalidStatusTransitionError) as exc_info:
        getattr(payment, second)()

    assert exc_info.value.message == f"Invalid payment status transition: {status.value} -> {target}"
    assert payment.status is status
    assert payment.timestamps.processed_at == processed_at
    assert payment.pull_events() == []


def test_pull_events_returns_recorded_events_only_once() -> None:
    payment = make_payment()
    payment.succeed()

    events = payment.pull_events()

    assert [type(event) for event in events] == [PaymentCreated, PaymentSucceeded]
    assert payment.pull_events() == []


def test_restored_payment_does_not_record_events() -> None:
    payment_id = PaymentID(UUID("123e4567-e89b-12d3-a456-426614174000"))
    created_at = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC)
    processed_at = datetime(2026, 10, 31, 12, 0, 3, tzinfo=UTC)
    metadata = {"order_id": 123}

    payment = Payment(
        payment_id=payment_id,
        idempotency_key=IdempotencyKey(IDEMPOTENCY_KEY),
        money=Money(Decimal("1500.00"), Currency.RUB),
        description=Description("Order #123"),
        webhook_url=WebhookURL("https://example.com/webhook"),
        status=PaymentStatus.succeeded,
        timestamps=PaymentTimestamps(created_at=created_at, processed_at=processed_at),
        metadata=metadata,
    )

    assert payment.payment_id == payment_id
    assert payment.status is PaymentStatus.succeeded
    assert payment.timestamps == PaymentTimestamps(created_at=created_at, processed_at=processed_at)
    assert payment.pull_events() == []

    metadata["order_id"] = 124
    assert payment.metadata == {"order_id": 123}
