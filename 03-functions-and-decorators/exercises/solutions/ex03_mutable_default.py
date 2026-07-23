"""SOLUTION 03-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


def add_item(item: str, cart: list[str] | None = None) -> list[str]:
    if cart is None:
        cart = []
    cart.append(item)
    return cart
