"""Spec for ex04_dataclass — make these pass."""

import pytest
from ex04_dataclass import Money


def test_currency_is_normalized_to_uppercase() -> None:
    assert Money(100, "usd").currency == "USD"


def test_normalization_makes_equality_work() -> None:
    assert Money(100, "usd") == Money(100, "USD")


def test_negative_amount_is_rejected() -> None:
    with pytest.raises(ValueError):
        Money(-1, "USD")


def test_currency_must_be_three_letters() -> None:
    with pytest.raises(ValueError):
        Money(100, "US")
    with pytest.raises(ValueError):
        Money(100, "USDX")


def test_frozen_like_a_record() -> None:
    money = Money(100, "USD")
    with pytest.raises(AttributeError):
        money.amount_cents = 200
