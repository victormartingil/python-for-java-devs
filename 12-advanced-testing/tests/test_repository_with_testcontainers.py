"""Repository tests against REAL PostgreSQL in a throwaway container ≈ @Testcontainers.

This is the top of the pyramid for a repository: no mocks, no fakes — the
actual SqlAlchemyTaskRepository from module 11 against an actual Postgres 16,
started and destroyed by testcontainers-python. Same discipline as
@DataJpaTest + @Testcontainers + @ServiceConnection in Spring Boot 3.

    @Container                              → postgres_container fixture (session scope)
    @ServiceConnection                      → the engine built from container host/port
    @Sql / cleanup between tests            → the `session` fixture truncates the table

Marked `docker`: skips cleanly when no Docker daemon is reachable (conftest.py).
Run just these:  uv run pytest -m docker -v
"""

from collections.abc import AsyncIterator, Iterator

import pytest
from app.core.database import Base
from app.tasks.models import TaskModel  # noqa: F401  (register the table on Base.metadata)
from app.tasks.repository import SqlAlchemyTaskRepository
from app.tasks.schemas import TaskCreate, TaskUpdate
from app.users.models import UserModel  # noqa: F401  (same shared metadata as the real app)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

pytestmark = pytest.mark.docker


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    """One container for the whole test session — ≈ the static @Container field.

    testcontainers waits for the DB to accept connections before yielding;
    `with` guarantees removal even if the suite crashes (Ryuk reaper).
    """
    with PostgresContainer("postgres:16", username="tasks", password="tasks", dbname="tasks") as pg:
        yield pg


@pytest.fixture
async def session(postgres_container: PostgresContainer) -> AsyncIterator[AsyncSession]:
    """A clean schema per test — ids reset, no state leaks between tests."""
    url = postgres_container.get_connection_url().replace("+psycopg2", "+asyncpg")
    engine = create_async_engine(url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as test_session:
        await test_session.execute(text("TRUNCATE TABLE tasks, users RESTART IDENTITY CASCADE"))
        await test_session.commit()
        yield test_session
    await engine.dispose()


@pytest.fixture
def repo(session: AsyncSession) -> SqlAlchemyTaskRepository:
    return SqlAlchemyTaskRepository(session)


async def test_create_assigns_id_and_defaults(repo: SqlAlchemyTaskRepository) -> None:
    record = await repo.create(TaskCreate(title="Real database!"))

    assert record.id == 1  # identity reset per test → deterministic
    assert record.completed is False
    assert record.description is None


async def test_list_filters_by_completed(repo: SqlAlchemyTaskRepository) -> None:
    await repo.create(TaskCreate(title="open"))
    await repo.create(TaskCreate(title="done", completed=True))

    all_tasks = await repo.list()
    only_done = await repo.list(completed=True)
    only_open = await repo.list(completed=False)

    assert [t.title for t in all_tasks] == ["open", "done"]  # ordered by id
    assert [t.title for t in only_done] == ["done"]
    assert [t.title for t in only_open] == ["open"]


async def test_get_missing_returns_none(repo: SqlAlchemyTaskRepository) -> None:
    assert await repo.get(999) is None


async def test_update_only_touches_set_fields(repo: SqlAlchemyTaskRepository) -> None:
    created = await repo.create(TaskCreate(title="before", description="keep me"))

    updated = await repo.update(created.id, TaskUpdate(completed=True))

    assert updated is not None
    assert updated.completed is True
    assert updated.title == "before"  # exclude_unset: title was NOT nulled
    assert updated.description == "keep me"


async def test_delete_is_idempotent_at_the_boundary(repo: SqlAlchemyTaskRepository) -> None:
    created = await repo.create(TaskCreate(title="ephemeral"))

    assert await repo.delete(created.id) is True
    assert await repo.delete(created.id) is False  # second delete: gone → False, not an error


async def test_roundtrip_survives_a_fresh_session(
    session: AsyncSession, repo: SqlAlchemyTaskRepository
) -> None:
    """Prove it's a REAL database: data written via one repo instance is visible
    to another instance sharing the committed transaction state."""
    await repo.create(TaskCreate(title="persisted"))
    await session.commit()  # repository only flush()es — commit happens at the boundary

    other_repo = SqlAlchemyTaskRepository(session)
    assert [t.title for t in await other_repo.list()] == ["persisted"]
