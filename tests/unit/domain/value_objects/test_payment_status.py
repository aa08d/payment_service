import pytest

from payment.domain.common.exceptions import DomainError
from payment.domain.payment.value_objects import PaymentStatus
from payment.domain.payment.value_objects.payment_status import InvalidStatusTransition, PaymentStatusError


def test_payment_status_has_only_supported_values() -> None:
    assert {status.value for status in PaymentStatus} == {"pending", "succeeded", "failed"}


def test_payment_status_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="paid"):
        PaymentStatus("paid")


def test_new_payment_status_is_pending() -> None:
    assert PaymentStatus.create() is PaymentStatus.pending


def test_pending_status_can_succeed() -> None:
    assert PaymentStatus.pending.succeed() is PaymentStatus.succeeded


def test_pending_status_can_fail() -> None:
    assert PaymentStatus.pending.fail() is PaymentStatus.failed


@pytest.mark.parametrize("status", [PaymentStatus.succeeded, PaymentStatus.failed])
def test_processed_status_cannot_succeed(status: PaymentStatus) -> None:
    with pytest.raises(InvalidStatusTransition) as exc_info:
        status.succeed()

    assert exc_info.value.message == f"Invalid payment status transition: {status.value} -> succeeded"


@pytest.mark.parametrize("status", [PaymentStatus.succeeded, PaymentStatus.failed])
def test_processed_status_cannot_fail(status: PaymentStatus) -> None:
    with pytest.raises(InvalidStatusTransition) as exc_info:
        status.fail()

    assert exc_info.value.message == f"Invalid payment status transition: {status.value} -> failed"


def test_invalid_status_transition_is_domain_error() -> None:
    assert issubclass(InvalidStatusTransition, PaymentStatusError)
    assert issubclass(InvalidStatusTransition, DomainError)


@pytest.mark.parametrize(
    ("status", "is_pending", "is_terminal"),
    [
        (PaymentStatus.pending, True, False),
        (PaymentStatus.succeeded, False, True),
        (PaymentStatus.failed, False, True),
    ],
)
def test_payment_status_flags(status: PaymentStatus, is_pending: bool, is_terminal: bool) -> None:
    assert status.is_pending is is_pending
    assert status.is_terminal is is_terminal


def test_payment_status_is_compared_with_string_value() -> None:
    assert PaymentStatus.succeeded == "succeeded"
    assert PaymentStatus("failed") is PaymentStatus.failed
