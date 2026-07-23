"""Repository tests against real PostgreSQL (≈ @DataJpaTest).

Marked `postgres`: they SKIP when no DB is reachable — see conftest.py.
Run them with:  docker compose up -d  &&  uv run pytest -m postgres
"""

import pytest
from persistapp.repository import TaskRepository
from persistapp.schemas import TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.postgres


@pytest.fixture
def repo(session: AsyncSession) -> TaskRepository:
    return TaskRepository(session)


async def test_create_assigns_id_and_roundtrips(repo: TaskRepository) -> None:
    task = await repo.create(TaskCreate(title="persist me", description="in postgres"))
    assert task.id == 1
    fetched = await repo.get(task.id)
    assert fetched is not None
    assert fetched.title == "persist me"
    assert fetched.completed is False


async def test_get_missing_returns_none(repo: TaskRepository) -> None:
    assert await repo.get(999) is None  # ≈ Optional.empty()


async def test_list_orders_by_id_and_filters(repo: TaskRepository) -> None:
    await repo.create(TaskCreate(title="a"))
    second = await repo.create(TaskCreate(title="b", completed=True))
    await repo.create(TaskCreate(title="c"))

    all_tasks = await repo.list()
    assert [t.title for t in all_tasks] == ["a", "b", "c"]

    completed = await repo.list(completed=True)
    assert [t.id for t in completed] == [second.id]


async def test_update_applies_only_sent_fields(repo: TaskRepository) -> None:
    task = await repo.create(TaskCreate(title="before", description="keep me"))
    updated = await repo.update(task, TaskUpdate(completed=True))
    assert updated.completed is True
    assert updated.title == "before"
    assert updated.description == "keep me"


async def test_delete_removes_row(repo: TaskRepository) -> None:
    task = await repo.create(TaskCreate(title="gone"))
    await repo.delete(task)
    assert await repo.get(task.id) is None
