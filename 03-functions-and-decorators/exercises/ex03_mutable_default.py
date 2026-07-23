"""Exercise 03-02 — the mutable default argument trap, fixed by you.

The trap: `def f(cart=[])` evaluates the default ONCE at function definition —
every call without that argument SHARES one list. See add_tag_wrong in
03-functions-and-decorators/decorators.py for the bug demonstrated live.

Implement add_item the safe way. The tests are the spec:

    uv run pytest 03-functions-and-decorators/exercises -v
"""


def add_item(item: str, cart: list[str] | None = None) -> list[str]:
    """Append item to cart and return the cart.

    - cart is None -> append to a FRESH list (each call independent)
    - cart given   -> append to THAT list object and return it (identity matters)

    The safe pattern: None as the default, create the mutable object inside.
    """
    raise NotImplementedError("TODO(ex02): `if cart is None: cart = []`, then append")
