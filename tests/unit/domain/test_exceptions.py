from datetime import UTC, datetime
from decimal import Decimal

import pytest

from payment.domain.common.exceptions import AppError, DomainError
from payment.domain.payment.value_objects.description import TooLongDescriptionError
from payment.domain.payment.value_objects.money import (
    NonFiniteAmountError,
    NonPositiveAmountError,
    TooManyFractionDigitsError,
)
from payment.domain.payment.value_objects.payment_status import InvalidStatusTransitionError
from payment.domain.payment.value_objects.payment_timestamps import PaymentAlreadyProcessedError
from payment.domain.payment.value_objects.webhook_url import InvalidWebhookURLError

DOMAIN_ERRORS = [
    NonFiniteAmountError(Decimal("NaN")),
    NonPositiveAmountError(Decimal("0")),
    TooManyFractionDigitsError(Decimal("0.001"), 2),
    TooLongDescriptionError("a" * 251),
    InvalidWebhookURLError("ftp://example.com"),
    InvalidStatusTransitionError("succeeded", "failed"),
    PaymentAlreadyProcessedError(datetime(2026, 10, 31, 12, 0, 3, tzinfo=UTC)),
]


@pytest.mark.parametrize("error", DOMAIN_ERRORS, ids=lambda error: type(error).__name__)
def test_domain_errors_are_unprocessable_and_have_readable_message(error: DomainError) -> None:
    assert isinstance(error, AppError)
    assert error.status == 422
    assert error.message
    assert error.message != DomainError().message
