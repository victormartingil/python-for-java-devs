"""PostgreSQL-dependent exercise tests — same discipline as the module's own.

Marked `postgres` tests SKIP cleanly when no database is reachable. Enable:
    cd 10-persistence-sqlalchemy-alembic && docker compose up -d
Point elsewhere with: DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
"""

import os
import socket
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from urllib.parse import urlparse

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # exercises/ (the stubs)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # module root (persistapp)

from persistapp.database import Base  # noqa: E402  (import after sys.path wiring)

DEFAULT_DATABASE_URL = "postgresql+asyncpg://tasks:tasks@localhost:5432/tasks"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def _postgres_reachable() -> bool:
    """Cheap TCP probe — no driver involved, sub-second timeout."""
    parsed = urlparse(database_url().replace("+asyncpg", ""))
    try:
        with socket.create_connection(
            (parsed.hostname or "localhost", parsed.port or 5432), timeout=0.5
        ):
            return True
    except OSError:
        return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if _postgres_reachable():
        return
    skip = pytest.mark.skip(
        reason="PostgreSQL not reachable — start it with `docker compose up -d` "
        "in 10-persistence-sqlalchemy-alembic/ (see README)"
    )
    for item in items:
        if "postgres" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """A clean database per test: schema ensured, table truncated (ids reset)."""
    engine = create_async_engine(database_url())
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as test_session:
        await test_session.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY"))
        await test_session.commit()
        yield test_session
    await engine.dispose()
