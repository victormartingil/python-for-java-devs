"""SOLUTION 05-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

import time
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def timer(timings: list[float]) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        timings.append(time.perf_counter() - start)
