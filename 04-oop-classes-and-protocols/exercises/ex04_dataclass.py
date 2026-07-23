"""Exercise 04-02 — a frozen dataclass with __post_init__ validation.

Finish the Money value object. The tests are the spec:

    uv run pytest 04-oop-classes-and-protocols/exercises -v

Hint: see Task in 04-oop-classes-and-protocols/notifiers.py (frozen=True ≈ a
Java record). __post_init__ runs right after the generated __init__ — the place
for validation and normalization, like a record's compact constructor.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """An amount in minor units (cents) + a 3-letter currency code.

    TODO(ex02): implement __post_init__ so that:
    - currency is normalized to UPPERCASE ("usd" -> "USD"). frozen=True blocks
      normal assignment — use object.__setattr__(self, "currency", ...).
    - currency must be exactly 3 letters  -> ValueError otherwise
    - amount_cents must be >= 0           -> ValueError otherwise
    """

    amount_cents: int
    currency: str

    def __post_init__(self) -> None:
        raise NotImplementedError("TODO(ex02): normalize + validate in __post_init__")
