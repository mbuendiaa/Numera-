from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from numera.domain.shared import (
    Currency,
    CurrencyMismatchError,
    InvalidMoneyAmountError,
    Money,
)


def test_money_normalizes_amount_to_two_decimal_places():
    assert Money("12.345", Currency.EUR).amount == Decimal("12.35")
    assert Money("12.344", Currency.EUR).amount == Decimal("12.34")


def test_money_is_immutable():
    money = Money("10.00", Currency.EUR)

    with pytest.raises(FrozenInstanceError):
        money.amount = Decimal("20.00")


def test_money_addition_and_subtraction():
    total = Money("100.00", Currency.EUR)
    payment = Money("30.45", Currency.EUR)

    assert total + payment == Money("130.45", Currency.EUR)
    assert total - payment == Money("69.55", Currency.EUR)


def test_money_comparisons_require_the_same_currency():
    assert Money("10.00", Currency.EUR) > Money("9.99", Currency.EUR)

    with pytest.raises(CurrencyMismatchError):
        Money("10.00", Currency.EUR) > Money("9.99", Currency.USD)


def test_money_operations_reject_different_currencies():
    eur = Money("10.00", Currency.EUR)
    usd = Money("10.00", Currency.USD)

    with pytest.raises(CurrencyMismatchError):
        eur + usd

    with pytest.raises(CurrencyMismatchError):
        eur - usd


def test_money_rejects_float_and_non_finite_amounts():
    with pytest.raises(InvalidMoneyAmountError):
        Money(10.50, Currency.EUR)

    with pytest.raises(InvalidMoneyAmountError):
        Money("NaN", Currency.EUR)

    with pytest.raises(InvalidMoneyAmountError):
        Money("Infinity", Currency.EUR)


def test_money_zero_sign_helpers_and_minor_units():
    zero = Money.zero(Currency.EUR)
    positive = Money.from_minor_units(1234, Currency.EUR)
    negative = -positive

    assert zero.is_zero()
    assert positive.is_positive()
    assert positive.amount == Decimal("12.34")
    assert positive.minor_units == 1234
    assert negative.is_negative()


def test_money_string_representation():
    assert str(Money("125.3", Currency.EUR)) == "125.30 EUR"
