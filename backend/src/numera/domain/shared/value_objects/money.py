"""Immutable monetary value object."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import total_ordering
from typing import Any

from numera.domain.shared.exceptions import (
    CurrencyMismatchError,
    InvalidMoneyAmountError,
)

from .currency import Currency

_CENT = Decimal("0.01")


@total_ordering
@dataclass(frozen=True, slots=True)
class Money:
    """A monetary amount expressed in one currency.

    Amounts are stored as ``Decimal`` and normalized to two decimal places.
    Floats are rejected so binary floating-point inaccuracies cannot enter the
    domain model silently.
    """

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        amount = self._normalize_amount(self.amount)
        currency = self._normalize_currency(self.currency)
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", currency)

    @classmethod
    def zero(cls, currency: Currency) -> Money:
        return cls(Decimal("0.00"), currency)

    @classmethod
    def from_minor_units(cls, minor_units: int, currency: Currency) -> Money:
        if isinstance(minor_units, bool) or not isinstance(minor_units, int):
            raise InvalidMoneyAmountError("Minor units must be an integer.")
        return cls(Decimal(minor_units) / 100, currency)

    @property
    def minor_units(self) -> int:
        return int(self.amount * 100)

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_positive(self) -> bool:
        return self.amount > Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")

    def __add__(self, other: Money) -> Money:
        self._require_money(other)
        self._require_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._require_money(other)
        self._require_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self) -> Money:
        return Money(-self.amount, self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: Money) -> bool:
        self._require_money(other)
        self._require_same_currency(other)
        return self.amount < other.amount

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency.value}"

    @staticmethod
    def _normalize_amount(value: Any) -> Decimal:
        if isinstance(value, bool) or isinstance(value, float):
            raise InvalidMoneyAmountError(
                "Money amount must be Decimal, int, or str; floats are not allowed."
            )

        if not isinstance(value, (Decimal, int, str)):
            raise InvalidMoneyAmountError(
                "Money amount must be Decimal, int, or str."
            )

        try:
            amount = value if isinstance(value, Decimal) else Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise InvalidMoneyAmountError(f"Invalid money amount: {value!r}.") from exc

        if not amount.is_finite():
            raise InvalidMoneyAmountError("Money amount must be finite.")

        return amount.quantize(_CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def _normalize_currency(value: Currency) -> Currency:
        if isinstance(value, Currency):
            return value
        try:
            return Currency(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Unsupported currency: {value!r}.") from exc

    @staticmethod
    def _require_money(other: object) -> None:
        if not isinstance(other, Money):
            raise TypeError("Money operations require another Money instance.")

    def _require_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot combine {self.currency.value} and {other.currency.value}."
            )
