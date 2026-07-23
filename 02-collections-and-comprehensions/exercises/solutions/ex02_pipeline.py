"""SOLUTION 02-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections import Counter
from typing import TypedDict


class Txn(TypedDict):
    category: str
    amount: int
    settled: bool


def total_by_category(txns: list[Txn]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for txn in txns:
        if txn["settled"]:
            totals[txn["category"]] += txn["amount"]
    return dict(totals)
