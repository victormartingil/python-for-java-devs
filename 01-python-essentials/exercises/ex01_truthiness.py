"""Exercise 01-02 — truthiness: the `or` trap with 0, and the emptiness shortcut.

Two small functions. The tests are the spec:

    uv run pytest 01-python-essentials/exercises -v

Anchor: Java has no truthiness — you write `!= null` and `!isEmpty()` explicitly.
Python treats 0, "", [], {}, None as falsy: perfect for emptiness checks,
dangerous when 0/"" are VALID values. See the "Truthiness" row in CHEATSHEET.md.
"""


def resolve_limit(configured: int | None, default: int) -> int:
    """Return `configured` when the caller set one, `default` otherwise.

    The trap: `return configured or default` looks right and breaks when
    configured == 0 — zero is a valid limit but falsy. Compare with `is not None`.
    (Java: configured != null ? configured : default)
    """
    raise NotImplementedError("TODO(ex02): return configured if it is not None, else default")


def describe_queue(pending: list[str]) -> str:
    """Return "queue is empty" when nothing is pending, else "<n> pending".

    Here truthiness is your friend: `if pending:` ≈ `if (!pending.isEmpty())`.
    """
    raise NotImplementedError("TODO(ex02): use truthiness — `if pending:`")
