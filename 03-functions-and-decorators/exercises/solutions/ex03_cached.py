"""SOLUTION 03-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

import functools
from collections.abc import Callable


def cached[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    cache: dict[tuple[tuple[object, ...], tuple[tuple[str, object], ...]], R] = {}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
