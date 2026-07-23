"""Tests for the tour functions — see module 07 for how pytest works."""

from tour import classify_http_status, first_long_word, greet


def test_greet_without_title() -> None:
    assert greet("Ada") == "Hello, Ada"


def test_greet_with_title() -> None:
    assert greet("Lovelace", title="Dr.") == "Hello, Dr. Lovelace"


def test_classify_http_status() -> None:
    assert classify_http_status(200) == "success"
    assert classify_http_status(404) == "not found"
    assert classify_http_status(418) == "client error"
    assert classify_http_status(503) == "server error"
    assert classify_http_status(100) == "other"


def test_first_long_word_uses_walrus() -> None:
    assert first_long_word(["hi", "hello"]) == "hello (5 chars)"
    assert first_long_word(["a", "b"]) is None
