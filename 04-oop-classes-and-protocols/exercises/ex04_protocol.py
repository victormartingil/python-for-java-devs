"""Exercise 04-01 — satisfy a Protocol without naming it.

StorageGateway is the contract (given). DictStorageGateway is yours: make it
satisfy the Protocol STRUCTURALLY — no inheritance, no import of the Protocol
into your class. The tests are the spec:

    uv run pytest 04-oop-classes-and-protocols/exercises -v

Hint: see EmailNotifier/SlackNotifier in 04-oop-classes-and-protocols/notifiers.py —
they never mention Notifier, yet notify_all() accepts them.
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
    """The adapter you are writing: a dict-backed StorageGateway.

    TODO(ex01): add put() and get() with the signatures the Protocol declares.
    Back them with the dict created in __init__. Do NOT inherit from
    StorageGateway — the match is structural (duck typing, verified).
    """

    def __init__(self) -> None:
        self._data: dict[str, str] = {}


def fetch_or_default(gateway: StorageGateway, key: str, default: str) -> str:
    """A consumer typed against the Protocol — given, working. Any object with
    the right shape is accepted, exactly like a Java interface parameter."""
    value = gateway.get(key)
    return value if value is not None else default
