from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from payment.domain.common.exceptions import DomainError
from payment.domain.common.value_objects import ValueObject

MAX_FRACTION_DIGITS = 2


class MoneyError(DomainError):
    pass


class NonFiniteAmountError(MoneyError):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount
        super().__init__(f"Amount must be a finite number, got {amount}.")


class NonPositiveAmountError(MoneyError):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount
        super().__init__(f"Amount must be greater than zero, got {amount}.")


class TooManyFractionDigitsError(MoneyError):
    def __init__(self, amount: Decimal, max_fraction_digits: int) -> None:
        self.amount = amount
        self.max_fraction_digits = max_fraction_digits
        super().__init__(
            f"Amount must have at most {max_fraction_digits} decimal places, "
            f"got {amount}."
        )


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


@dataclass(frozen=True)
class Money(ValueObject):
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not self.amount.is_finite():
            raise NonFiniteAmountError(self.amount)

        if self.amount <= 0:
            raise NonPositiveAmountError(self.amount)

        exponent = self.amount.as_tuple().exponent
        if isinstance(exponent, int) and exponent < -MAX_FRACTION_DIGITS:
            raise TooManyFractionDigitsError(self.amount, MAX_FRACTION_DIGITS)
