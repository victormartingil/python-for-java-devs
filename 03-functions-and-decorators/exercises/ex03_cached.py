"""Exercise 03-01 — write a decorator from scratch: @cached.

A decorator is a function that takes a function and returns a function.
Implement memoization: one real evaluation per unique argument combination.
The tests are the spec:

    uv run pytest 03-functions-and-decorators/exercises -v

Hint: see @timed and @retry in 03-functions-and-decorators/decorators.py —
the skeleton (wrapper + functools.wraps) is identical; only the body differs.
The `[**P, R]` syntax (PEP 695) preserves the wrapped signature for mypy.
You'll need `import functools` for the wraps part.
"""

from collections.abc import Callable


def cached[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Memoize `func`: cache on (args, sorted kwargs); repeat calls with the same
    arguments return the stored result WITHOUT re-invoking func.

    Java anchor: hand-written AOP caching around a method — except here YOU
    write the advice. Assume hashable arguments only.

    Requirements:
    - one evaluation per unique call signature
    - results cached per decorated function (not one global cache)
    - __name__/__doc__ survive via functools.wraps
    """
    raise NotImplementedError("TODO(ex01): wrapper function + dict cache + functools.wraps")
