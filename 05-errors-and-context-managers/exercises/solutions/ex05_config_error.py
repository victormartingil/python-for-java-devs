"""SOLUTION 05-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""


class ConfigError(Exception):
    """Raised when configuration input is invalid (≈ a domain/infra exception)."""


def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise ConfigError(f"invalid port value: {value!r}") from exc
    if not 1 <= port <= 65535:
        raise ConfigError(f"port out of range (1-65535): {value!r}")
    return port
