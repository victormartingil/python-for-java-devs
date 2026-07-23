"""Exercise 02-03 — a Streams pipeline, translated.

Java:    txns.stream().filter(Txn::isSettled)
             .collect(groupingBy(Txn::getCategory, summingInt(Txn::getAmount)));
Python:  pick your weapon — a Counter, or a plain loop with dict.get.
         No streams, no indexes. The tests are the spec:

    uv run pytest 02-collections-and-comprehensions/exercises -v

Hint: see counts_by_priority and titles_by_status in
02-collections-and-comprehensions/collections_demo.py.
"""

from typing import TypedDict


class Txn(TypedDict):
    category: str
    amount: int
    settled: bool


def total_by_category(txns: list[Txn]) -> dict[str, int]:
    """Sum the amounts of SETTLED transactions per category.

    Unsettled transactions don't count. No transactions -> {}.
    """
    raise NotImplementedError("TODO(ex03): filter settled, then group + sum by category")
