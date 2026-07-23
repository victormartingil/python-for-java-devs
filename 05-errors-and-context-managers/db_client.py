"""Errors & context managers — a simulated DB client with `with`.

Run it:
    uv run python 05-errors-and-context-managers/db_client.py
"""

from collections.abc import Iterator
from contextlib import contextmanager


# --- Domain exceptions: one line each, meaning in the name ---------------------
class RepositoryError(Exception):
    """Base for storage failures (≈ DataAccessException)."""


class EntityNotFoundError(RepositoryError):
    """Raised when a lookup misses."""


class ClientClosedError(RepositoryError):
    """Raised when using a closed connection."""


# --- 1. Context manager, the class way (≈ AutoCloseable) ------------------------
class FakeDbClient:
    """A pretend DB client: connect/close lifecycle + a dict for storage."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.connected = False
        self._rows: dict[int, str] = {}

    def __enter__(self) -> "FakeDbClient":
        self.connected = True  # acquire the resource
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.connected = False  # release it — even if an exception flew
        # returning None (falsy) = don't swallow the exception

    def insert(self, row_id: int, payload: str) -> None:
        if not self.connected:
            raise ClientClosedError("insert on a closed client")
        self._rows[row_id] = payload

    def get(self, row_id: int) -> str:
        if not self.connected:
            raise ClientClosedError("get on a closed client")
        try:
            return self._rows[row_id]
        except KeyError:
            # EAFP + exception translation (≈ Spring's DataAccessException mapping)
            raise EntityNotFoundError(f"no row with id={row_id}") from None


# --- 2. Context manager, the @contextmanager way (usually what you want) --------
@contextmanager
def transaction(client: FakeDbClient) -> Iterator[FakeDbClient]:
    """Commit on success, rollback on exception — acquire/try/release as a recipe."""
    tx_log.append("begin")
    try:
        yield client  # whatever follows `as` in the `with` statement
    except Exception:
        tx_log.append("rollback")
        raise
    else:
        tx_log.append("commit")


tx_log: list[str] = []  # simple observable log for the demo and tests


# --- 3. EAFP vs LBYL, side by side ----------------------------------------------
def get_or_default_lbyl(rows: dict[int, str], row_id: int) -> str:
    """Look Before You Leap — the Java instinct."""
    if row_id in rows:
        return rows[row_id]
    return "<default>"


def get_or_default_eafp(rows: dict[int, str], row_id: int) -> str:
    """Easier to Ask Forgiveness than Permission — the Python instinct."""
    try:
        return rows[row_id]
    except KeyError:
        return "<default>"


def main() -> None:
    # try-with-resources, Python edition:
    with FakeDbClient("postgres://localhost/demo") as db:
        db.insert(1, "first task")
        print("fetched:", db.get(1))
        try:
            db.get(999)
        except EntityNotFoundError as exc:
            print("caught domain error:", exc)
    print("client connected after `with`?", db.connected)  # False — auto-closed

    # Transactional recipe:
    with FakeDbClient("postgres://localhost/demo") as db:
        with transaction(db):
            db.insert(2, "committed work")
        try:
            with transaction(db):
                raise RuntimeError("boom mid-transaction")
        except RuntimeError:
            pass
    print("tx log:", tx_log)  # ['begin', 'commit', 'begin', 'rollback']

    print("LBYL:", get_or_default_lbyl({}, 7), "| EAFP:", get_or_default_eafp({}, 7))


if __name__ == "__main__":
    main()
