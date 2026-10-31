from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from payment.domain.common.exceptions import DomainError
from payment.domain.payment.value_objects import Currency, Money
from payment.domain.payment.value_objects.money import (
    MoneyError,
    NonFiniteAmountError,
    NonPositiveAmountError,
    TooManyFractionDigitsError,
)


@pytest.mark.parametrize("amount", ["0.01", "1", "1500.00", "99999999999999.99", "1E+2"])
def test_money_accepts_positive_amount_with_up_to_two_fraction_digits(amount: str) -> None:
    money = Money(Decimal(amount), Currency.RUB)

    assert money.amount == Decimal(amount)
    assert money.currency is Currency.RUB


@pytest.mark.parametrize("amount", ["0", "0.00", "-1", "-0.01"])
def test_money_rejects_zero_and_negative_amount(amount: str) -> None:
    with pytest.raises(NonPositiveAmountError):
        Money(Decimal(amount), Currency.RUB)


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-Infinity"])
def test_money_rejects_non_finite_amount(amount: str) -> None:
    with pytest.raises(NonFiniteAmountError):
        Money(Decimal(amount), Currency.RUB)


@pytest.mark.parametrize("amount", ["0.001", "1.234", "10.005"])
def test_money_rejects_more_than_two_fraction_digits(amount: str) -> None:
    with pytest.raises(TooManyFractionDigitsError) as exc_info:
        Money(Decimal(amount), Currency.RUB)

    assert exc_info.value.max_fraction_digits == 2


def test_money_error_describes_invalid_amount() -> None:
    with pytest.raises(NonPositiveAmountError) as exc_info:
        Money(Decimal("-5"), Currency.USD)

    assert exc_info.value.amount == Decimal("-5")
    assert "greater than zero" in exc_info.value.message
    assert "-5" in exc_info.value.message


@pytest.mark.parametrize("error", [NonFiniteAmountError, NonPositiveAmountError, TooManyFractionDigitsError])
def test_money_errors_are_domain_errors(error: type[Exception]) -> None:
    assert issubclass(error, MoneyError)
    assert issubclass(error, DomainError)


def test_currency_has_only_supported_values() -> None:
    assert {currency.value for currency in Currency} == {"RUB", "USD", "EUR"}


def test_currency_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="GBP"):
        Currency("GBP")


def test_money_equality_depends_on_amount_and_currency() -> None:
    assert Money(Decimal("10.00"), Currency.RUB) == Money(Decimal("10.00"), Currency.RUB)
    assert Money(Decimal("10.00"), Currency.RUB) == Money(Decimal("10"), Currency.RUB)
    assert Money(Decimal("10.00"), Currency.RUB) != Money(Decimal("10.00"), Currency.USD)
    assert Money(Decimal("10.00"), Currency.RUB) != Money(Decimal("10.01"), Currency.RUB)


def test_money_is_immutable() -> None:
    money = Money(Decimal("10.00"), Currency.RUB)

    with pytest.raises(FrozenInstanceError):
        money.amount = Decimal("20.00")  # type: ignore[misc]
