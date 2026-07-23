"""Exercise 05-01 — a custom exception + EAFP translation.

Implement parse_port. The tests are the spec:

    uv run pytest 05-errors-and-context-managers/exercises -v

Anchor: Spring translates low-level exceptions into DataAccessException — same
move here: ValueError -> ConfigError, chained with `raise ... from exc` (≈
initCause). And it's EAFP: try the conversion, handle failure — don't
pre-validate with if-checks (that's LBYL). See get() and get_or_default_eafp
in 05-errors-and-context-managers/db_client.py.
"""


class ConfigError(Exception):
    """Raised when configuration input is invalid (≈ a domain/infra exception)."""


def parse_port(value: str) -> int:
    """Parse `value` into a TCP port number (1–65535).

    - "8080"  -> 8080
    - "abc"   -> ConfigError (translate the ValueError, chain it with `from`)
    - "0"     -> ConfigError (out of range)
    - "65536" -> ConfigError (out of range)

    The ConfigError message must include the offending value.
    """
    raise NotImplementedError("TODO(ex01): try int(value), translate ValueError, range-check")
