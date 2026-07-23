"""SOLUTION 04-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount_cents: int
    currency: str

    def __post_init__(self) -> None:
        normalized = self.currency.upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError(f"currency must be a 3-letter code, got {self.currency!r}")
        if self.amount_cents < 0:
            raise ValueError(f"amount_cents must be >= 0, got {self.amount_cents}")
        object.__setattr__(self, "currency", normalized)
