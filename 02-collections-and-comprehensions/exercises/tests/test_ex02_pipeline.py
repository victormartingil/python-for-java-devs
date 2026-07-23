"""Spec for ex02_pipeline — make these pass."""

from ex02_pipeline import Txn, total_by_category

TXNS: list[Txn] = [
    {"category": "infra", "amount": 100, "settled": True},
    {"category": "travel", "amount": 50, "settled": True},
    {"category": "infra", "amount": 25, "settled": True},
    {"category": "travel", "amount": 999, "settled": False},  # pending — must not count
]


def test_sums_settled_amounts_per_category() -> None:
    assert total_by_category(TXNS) == {"infra": 125, "travel": 50}


def test_unsettled_transactions_are_excluded() -> None:
    assert 999 not in total_by_category(TXNS).values()


def test_empty_input() -> None:
    assert total_by_category([]) == {}
