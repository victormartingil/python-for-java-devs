"""Spec for ex03_forwarding — make these pass."""

from ex03_forwarding import call_safely


def add(a: int, b: int) -> int:
    return a + b


def greet(name: str, title: str = "Mx.") -> str:
    return f"{title} {name}"


def explode() -> str:
    raise ValueError("boom")


def test_positional_args_are_forwarded() -> None:
    assert call_safely(add, 2, 3) == (5, None)


def test_kwargs_and_defaults_are_forwarded() -> None:
    assert call_safely(greet, "ada") == ("Mx. ada", None)
    assert call_safely(greet, "ada", title="Dr.") == ("Dr. ada", None)


def test_exception_is_captured_not_raised() -> None:
    result, error = call_safely(explode)
    assert result is None
    assert error == "boom"
