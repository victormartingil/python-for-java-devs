"""Spec for ex05_config_error — make these pass."""

import pytest
from ex05_config_error import ConfigError, parse_port


def test_valid_port() -> None:
    assert parse_port("8080") == 8080


def test_boundary_ports() -> None:
    assert parse_port("1") == 1
    assert parse_port("65535") == 65535


def test_non_numeric_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        parse_port("abc")


def test_out_of_range_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        parse_port("0")
    with pytest.raises(ConfigError):
        parse_port("65536")


def test_error_message_names_the_offending_value() -> None:
    with pytest.raises(ConfigError, match="banana"):
        parse_port("banana")


def test_cause_is_chained_like_init_cause() -> None:
    # raise ... from exc ≈ Java's initCause: the original error stays attached.
    with pytest.raises(ConfigError) as exc_info:
        parse_port("abc")
    assert isinstance(exc_info.value.__cause__, ValueError)
