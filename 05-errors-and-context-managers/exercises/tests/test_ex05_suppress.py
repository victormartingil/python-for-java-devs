"""Spec for ex05_suppress — make these pass."""

from ex05_suppress import log_and_continue


def test_exception_is_swallowed_and_logged() -> None:
    log: list[str] = []
    with log_and_continue(log, "send metrics"):
        raise ConnectionError("connection refused")
    assert len(log) == 1
    assert "send metrics" in log[0]
    assert "connection refused" in log[0]


def test_clean_block_logs_nothing() -> None:
    log: list[str] = []
    with log_and_continue(log, "send metrics"):
        pass
    assert log == []


def test_execution_continues_after_the_block() -> None:
    log: list[str] = []
    reached = False
    with log_and_continue(log, "op"):
        raise ValueError("nope")
    reached = True
    assert reached
