"""SOLUTION 05-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def log_and_continue(log: list[str], operation: str) -> Iterator[None]:
    try:
        yield
    except Exception as exc:
        log.append(f"{operation} failed: {exc}")
