"""Exercise 05-02 — write a context manager: timing with @contextmanager.

Implement timer. The tests are the spec:

    uv run pytest 05-errors-and-context-managers/exercises -v

Anchor: try-with-resources acquires/releases around a block; @contextmanager
writes that recipe as a generator — code before `yield` = acquire, code after
= release. See transaction() in 05-errors-and-context-managers/db_client.py.
You'll need `import time` for the measurement.
"""

from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def timer(timings: list[float]) -> Iterator[None]:
    """Measure the with-block: append the elapsed seconds (a float) to `timings`.

    Must record even when the block raises — and let the exception propagate
    (don't swallow it: re-raise, or simply don't catch).

    Usage:
        timings: list[float] = []
        with timer(timings):
            ...  # work
    """
    raise NotImplementedError("TODO(ex02): perf_counter around the yield, append elapsed")
