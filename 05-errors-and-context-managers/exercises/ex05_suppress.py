"""Exercise 05-03 — suppress-and-log: a scoped catch-and-log.

Implement log_and_continue. The tests are the spec:

    uv run pytest 05-errors-and-context-managers/exercises -v

Anchor: Java code sometimes wraps a non-critical step in try/catch and just
logs the failure. This context manager scopes that pattern to one block —
useful sparingly, dangerous when overused (like empty catch blocks).
"""

from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def log_and_continue(log: list[str], operation: str) -> Iterator[None]:
    """Run the with-block; if it raises, swallow the exception and append
    f"{operation} failed: {exc}" to `log`. No exception -> no log entry.

    Use try/except around the yield — same skeleton as transaction() in
    05-errors-and-context-managers/db_client.py, minus the re-raise.
    """
    raise NotImplementedError("TODO(ex03): catch around the yield, append, don't re-raise")
