"""SOLUTION 04-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from typing import Protocol


class StorageGateway(Protocol):
    """≈ a Java interface — but implementations don't have to name it."""

    def put(self, key: str, value: str) -> None:
        """Store value under key, overwriting any previous value."""
        ...

    def get(self, key: str) -> str | None:
        """Return the stored value, or None when the key is unknown."""
        ...


class DictStorageGateway:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def put(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str) -> str | None:
        return self._data.get(key)


def fetch_or_default(gateway: StorageGateway, key: str, default: str) -> str:
    """A consumer typed against the Protocol — given, working. Any object with
    the right shape is accepted, exactly like a Java interface parameter."""
    value = gateway.get(key)
    return value if value is not None else default
