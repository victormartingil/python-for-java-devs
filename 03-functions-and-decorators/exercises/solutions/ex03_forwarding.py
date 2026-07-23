"""SOLUTION 03-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Callable


def call_safely[**P, R](
    func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> tuple[R | None, str | None]:
    try:
        return func(*args, **kwargs), None
    except Exception as exc:
        return None, str(exc)
