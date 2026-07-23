"""Spec for ex01_truthiness — make these pass."""

from ex01_truthiness import describe_queue, resolve_limit


def test_configured_limit_wins() -> None:
    assert resolve_limit(25, 10) == 25


def test_zero_is_a_valid_limit() -> None:
    # `configured or default` returns 10 here — that's the bug this exercise kills.
    assert resolve_limit(0, 10) == 0


def test_none_falls_back_to_default() -> None:
    assert resolve_limit(None, 10) == 10


def test_empty_queue() -> None:
    assert describe_queue([]) == "queue is empty"


def test_non_empty_queue() -> None:
    assert describe_queue(["a", "b", "c"]) == "3 pending"
