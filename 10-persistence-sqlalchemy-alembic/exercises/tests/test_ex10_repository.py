"""Spec for ex01 (count + pagination) — postgres-marked, skips without a DB."""

import pytest
from ex10_repository import ExtendedTaskRepository
from persistapp.schemas import TaskCreate
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.postgres


@pytest.fixture
def repo(session: AsyncSession) -> ExtendedTaskRepository:
    return ExtendedTaskRepository(session)


async def test_count_empty(repo: ExtendedTaskRepository) -> None:
    assert await repo.count() == 0


async def test_count_all_and_filtered(repo: ExtendedTaskRepository) -> None:
    await repo.create(TaskCreate(title="a"))
    await repo.create(TaskCreate(title="b", completed=True))
    await repo.create(TaskCreate(title="c"))
    assert await repo.count() == 3
    assert await repo.count(completed=True) == 1
    assert await repo.count(completed=False) == 2


async def test_list_page_returns_rows_in_id_order(repo: ExtendedTaskRepository) -> None:
    for letter in ("a", "b", "c", "d"):
        await repo.create(TaskCreate(title=letter))
    first_page = await repo.list_page(limit=2)
    assert [t.title for t in first_page] == ["a", "b"]


async def test_list_page_offset_continues(repo: ExtendedTaskRepository) -> None:
    for letter in ("a", "b", "c", "d"):
        await repo.create(TaskCreate(title=letter))
    second_page = await repo.list_page(limit=2, offset=2)
    assert [t.title for t in second_page] == ["c", "d"]


async def test_list_page_beyond_the_end_is_empty(repo: ExtendedTaskRepository) -> None:
    await repo.create(TaskCreate(title="a"))
    assert list(await repo.list_page(limit=10, offset=10)) == []
