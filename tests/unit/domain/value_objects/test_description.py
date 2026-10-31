from dataclasses import FrozenInstanceError

import pytest

from payment.domain.common.exceptions import DomainError
from payment.domain.payment.value_objects import Description
from payment.domain.payment.value_objects.description import (
    MAX_DESCRIPTION_LENGTH,
    DescriptionError,
    TooLongDescriptionError,
)


def test_description_accepts_usual_text() -> None:
    assert Description("Order #123").value == "Order #123"


def test_description_accepts_empty_text() -> None:
    assert Description("").value == ""


def test_description_accepts_maximum_length() -> None:
    description = Description("a" * MAX_DESCRIPTION_LENGTH)

    assert len(description.value) == MAX_DESCRIPTION_LENGTH


def test_description_rejects_text_longer_than_maximum() -> None:
    with pytest.raises(TooLongDescriptionError):
        Description("a" * (MAX_DESCRIPTION_LENGTH + 1))


def test_description_length_is_counted_in_characters_not_bytes() -> None:
    assert len(Description("я" * MAX_DESCRIPTION_LENGTH).value) == MAX_DESCRIPTION_LENGTH

    with pytest.raises(TooLongDescriptionError):
        Description("я" * (MAX_DESCRIPTION_LENGTH + 1))


def test_description_error_reports_limit_and_actual_length() -> None:
    with pytest.raises(TooLongDescriptionError) as exc_info:
        Description("a" * 300)

    assert isinstance(exc_info.value, DescriptionError)
    assert isinstance(exc_info.value, DomainError)
    assert str(MAX_DESCRIPTION_LENGTH) in exc_info.value.message
    assert "300" in exc_info.value.message


def test_description_equality_depends_on_value() -> None:
    assert Description("a") == Description("a")
    assert Description("a") != Description("b")


def test_description_is_immutable() -> None:
    description = Description("a")

    with pytest.raises(FrozenInstanceError):
        description.value = "b"  # type: ignore[misc]
