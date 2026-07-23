"""Functions & decorators — building `@timed` and `@retry` from scratch.

A decorator is a function that takes a function and returns a function.
That's the whole trick. Everything else (@app.get, @pytest.fixture,
@dataclass) is this same pattern with different clothes.

Run it:
    uv run python 03-functions-and-decorators/decorators.py
"""

import functools
import time
from collections.abc import Callable

# The `[**P, R]` syntax below is PEP 695 (Python 3.12+): inline generic type
# parameters — P is "the parameters of the wrapped function, whatever they
# are", R is "its return type". Together they preserve the full signature.
# (Older code does the same with ParamSpec/TypeVar from `typing`.)


# --- 1. A simple decorator: @timed ------------------------------------------
def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Decorator ≈ @Around advice: runs code before/after the target."""

    @functools.wraps(func)  # keep __name__/__doc__ — always do this
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"  [timed] {func.__name__} took {elapsed_ms:.1f} ms")
        return result

    return wrapper


# --- 2. A decorator with arguments: @retry(times=3) ---------------------------
# @retry(times=3) means: retry(times=3) -> returns a decorator -> wraps func.
# Same as an annotation with attributes: @Retry(times = 3) in Spring Retry.
def retry[**P, R](
    times: int = 3, exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry the wrapped function up to `times` on the given exceptions."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    print(f"  [retry] {func.__name__} attempt {attempt}/{times} failed")
            raise AssertionError("unreachable")  # keeps mypy happy

        return wrapper

    return decorator


# --- 3. The mutable default trap ----------------------------------------------
def add_tag_wrong(task: str, tags: list[str] = []) -> list[str]:  # noqa: B006
    """DON'T: the default list is created ONCE and shared across all calls."""
    tags.append(task)
    return tags


def add_tag(task: str, tags: list[str] | None = None) -> list[str]:
    """DO: None as default, create the mutable object inside."""
    tags = [] if tags is None else tags
    tags.append(task)
    return tags


# --- 4. Putting it together -----------------------------------------------------
@timed
@retry(times=3, exceptions=(ConnectionError,))
def flaky_remote_call(failures_left: list[int]) -> str:
    """Simulates a flaky service: fails while there are failures left."""
    if failures_left:
        failures_left.pop()
        raise ConnectionError("simulated network failure")
    return "payload from remote service"


def main() -> None:
    print("--- the mutable default trap ---")
    print(add_tag_wrong("urgent"))  # ['urgent']
    print(add_tag_wrong("later"))  # ['urgent', 'later'] ← leaked from the previous call!
    print(add_tag("urgent"))  # ['urgent'] — fresh list every call
    print(add_tag("later"))  # ['later']

    print("--- decorators ≈ AOP ---")
    failures = [1, 2]  # two simulated failures, then success
    result = flaky_remote_call(failures_left=failures)
    print(f"  result: {result}")
    # Thanks to functools.wraps, metadata survives the wrappers:
    print(f"  name intact: {flaky_remote_call.__name__}")


if __name__ == "__main__":
    main()
