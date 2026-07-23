import pytest
from decorators import add_tag, add_tag_wrong, flaky_remote_call, retry, timed


def test_timed_returns_result_and_preserves_name() -> None:
    @timed
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
    assert add.__name__ == "add"  # functools.wraps did its job


def test_retry_succeeds_after_failures() -> None:
    assert flaky_remote_call(failures_left=[1, 2]) == "payload from remote service"


def test_retry_gives_up_after_max_attempts() -> None:
    with pytest.raises(ConnectionError):
        flaky_remote_call(failures_left=[1, 2, 3, 4])  # more failures than retries


def test_retry_with_zero_failures() -> None:
    @retry(times=2)
    def ok() -> str:
        return "fine"

    assert ok() == "fine"


def test_mutable_default_trap_is_real() -> None:
    add_tag_wrong("a")
    leaked = add_tag_wrong("b")
    assert leaked == ["a", "b"]  # state leaked across calls — the bug, demonstrated


def test_safe_default_does_not_leak() -> None:
    assert add_tag("a") == ["a"]
    assert add_tag("b") == ["b"]
