"""Exercise 03-03 — *args/**kwargs: forwarding an arbitrary signature.

call_safely invokes any function with any arguments and reports the outcome
without raising. The tests are the spec:

    uv run pytest 03-functions-and-decorators/exercises -v

Hint: the wrapper inside @timed in 03-functions-and-decorators/decorators.py
forwards *args/**kwargs exactly like this. `[**P, R]` (PEP 695) types it.
"""

from collections.abc import Callable


def call_safely[**P, R](
    func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> tuple[R | None, str | None]:
    """Call func(*args, **kwargs).

    Return (result, None) on success, (None, str(exception)) on failure.
    Java anchor: a tiny invoke-and-translate boundary — EAFP, not LBYL.
    """
    raise NotImplementedError("TODO(ex03): try/except around func(*args, **kwargs)")
