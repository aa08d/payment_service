from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from payment.domain.common.exceptions import DomainError
from payment.domain.payment.value_objects import PaymentTimestamps
from payment.domain.payment.value_objects.payment_timestamps import PaymentAlreadyProcessedError


def test_new_timestamps_have_creation_time_and_no_processing_time() -> None:
    before = datetime.now(UTC)
    timestamps = PaymentTimestamps.create()
    after = datetime.now(UTC)

    assert before <= timestamps.created_at <= after
    assert timestamps.created_at.tzinfo is UTC
    assert timestamps.processed_at is None


def test_mark_processed_sets_processing_time_and_keeps_creation_time() -> None:
    timestamps = PaymentTimestamps.create()

    before = datetime.now(UTC)
    processed = timestamps.mark_processed()
    after = datetime.now(UTC)

    assert processed.created_at == timestamps.created_at
    assert processed.processed_at is not None
    assert before <= processed.processed_at <= after
    assert processed.processed_at.tzinfo is UTC
    assert processed.processed_at >= processed.created_at


def test_mark_processed_does_not_change_original_timestamps() -> None:
    timestamps = PaymentTimestamps.create()

    timestamps.mark_processed()

    assert timestamps.processed_at is None


def test_payment_cannot_be_marked_processed_twice() -> None:
    processed = PaymentTimestamps.create().mark_processed()

    with pytest.raises(PaymentAlreadyProcessedError) as exc_info:
        processed.mark_processed()

    assert processed.processed_at is not None
    assert processed.processed_at.isoformat() in exc_info.value.message
    assert isinstance(exc_info.value, DomainError)


def test_timestamps_are_immutable() -> None:
    timestamps = PaymentTimestamps.create()

    with pytest.raises(FrozenInstanceError):
        timestamps.processed_at = datetime.now(UTC)  # type: ignore[misc]
