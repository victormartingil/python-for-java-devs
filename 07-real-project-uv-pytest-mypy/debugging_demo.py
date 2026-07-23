"""Debugging playground: order stats with a deliberate bug.

Run:  uv run python 07-real-project-uv-pytest-mypy/debugging_demo.py

The bug: `average_order_value` divides by the number of *lines*, not the
number of *orders* — find it with `breakpoint()` (line marked below), with
`uv run pytest --pdb` on your own failing test, or with your IDE's debugger
(see the "Debugging & profiling" section of this module's README).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
    lines: list[float]

    @property
    def total(self) -> float:
        return sum(self.lines)


def average_order_value(orders: list[Order]) -> float:
    if not orders:
        return 0.0
    grand_total = sum(order.total for order in orders)
    # breakpoint()  # <-- uncomment me, run the script, then: pp orders / grand_total
    divisor = sum(len(order.lines) for order in orders)  # BUG: should be len(orders)
    return grand_total / divisor


def top_order(orders: list[Order]) -> Order | None:
    """≈ stream().max(comparing(Order::total)).orElse(null) — with a key function."""
    return max(orders, key=lambda order: order.total, default=None)


def main() -> None:
    orders = [
        Order(id=1, lines=[25.0, 15.0]),
        Order(id=2, lines=[60.0]),
        Order(id=3, lines=[10.0, 10.0, 20.0, 10.0]),
    ]
    best = top_order(orders)
    print(f"orders: {len(orders)}, grand total: {sum(o.total for o in orders):.2f}")
    print(f"top order: #{best.id if best else '-'}")
    # Expected 50.00 (150 / 3 orders) — the bug prints 21.43 (150 / 7 lines) instead:
    print(f"average order value: {average_order_value(orders):.2f}")


if __name__ == "__main__":
    main()
