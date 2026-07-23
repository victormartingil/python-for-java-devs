"""Spec for ex01_match — make these pass."""

from ex01_match import retry_decision


def test_success_statuses_are_ok() -> None:
    assert retry_decision(200) == "ok"
    assert retry_decision(201) == "ok"
    assert retry_decision(204) == "ok"


def test_rate_limited_retries_after_delay() -> None:
    assert retry_decision(429) == "retry after delay"


def test_server_errors_retry() -> None:
    for code in (500, 502, 503, 504):
        assert retry_decision(code) == "retry", f"{code} should retry"


def test_other_client_errors_fail_fast() -> None:
    assert retry_decision(400) == "fail fast"
    assert retry_decision(404) == "fail fast"
    assert retry_decision(418) == "fail fast"


def test_anything_else_is_unknown() -> None:
    assert retry_decision(100) == "unknown"
    assert retry_decision(302) == "unknown"
