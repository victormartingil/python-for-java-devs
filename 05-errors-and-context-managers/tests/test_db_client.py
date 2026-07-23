import pytest
from db_client import (
    ClientClosedError,
    EntityNotFoundError,
    FakeDbClient,
    get_or_default_eafp,
    get_or_default_lbyl,
    transaction,
    tx_log,
)


def test_with_block_closes_client() -> None:
    with FakeDbClient("dsn") as db:
        assert db.connected
    assert not db.connected  # closed even on the way out


def test_client_closes_even_on_exception() -> None:
    db = FakeDbClient("dsn")
    with pytest.raises(RuntimeError), db:
        raise RuntimeError("boom")
    assert not db.connected


def test_get_missing_raises_domain_exception() -> None:
    with FakeDbClient("dsn") as db, pytest.raises(EntityNotFoundError, match="id=999"):
        db.get(999)


def test_using_closed_client_fails_fast() -> None:
    db = FakeDbClient("dsn")
    with pytest.raises(ClientClosedError):
        db.get(1)


def test_transaction_commit_and_rollback() -> None:
    tx_log.clear()
    with FakeDbClient("dsn") as db:
        with transaction(db):
            db.insert(1, "ok")
        with pytest.raises(ValueError), transaction(db):
            raise ValueError("fail")
    assert tx_log == ["begin", "commit", "begin", "rollback"]


def test_eafp_and_lbyl_agree() -> None:
    rows = {1: "a"}
    assert get_or_default_eafp(rows, 1) == get_or_default_lbyl(rows, 1) == "a"
    assert get_or_default_eafp(rows, 9) == get_or_default_lbyl(rows, 9) == "<default>"
