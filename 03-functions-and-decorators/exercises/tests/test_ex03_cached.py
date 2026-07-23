"""Spec for ex03_cached — make these pass."""

from ex03_cached import cached


def test_result_is_correct() -> None:
    @cached
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5


def test_underlying_function_runs_once_per_unique_args() -> None:
    calls: list[int] = []

    @cached
    def slow_square(n: int) -> int:
        calls.append(n)
        return n * n

    assert slow_square(4) == 16
    assert slow_square(4) == 16
    assert calls == [4], "the second call with the same args must hit the cache"


def test_different_args_are_separate_cache_entries() -> None:
    calls: list[int] = []

    @cached
    def double(n: int) -> int:
        calls.append(n)
        return 2 * n

    assert double(2) == 4
    assert double(3) == 6
    assert double(2) == 4
    assert calls == [2, 3]


def test_kwargs_participate_in_the_cache_key() -> None:
    calls: list[tuple[str, str]] = []

    @cached
    def greet(name: str, greeting: str = "hi") -> str:
        calls.append((name, greeting))
        return f"{greeting} {name}"

    assert greet("ada") == "hi ada"
    assert greet("ada") == "hi ada"
    assert greet("ada", greeting="yo") == "yo ada"
    assert calls == [("ada", "hi"), ("ada", "yo")]


def test_name_and_docstring_survive() -> None:
    @cached
    def documented() -> str:
        """I am documented."""
        return "x"

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "I am documented."
