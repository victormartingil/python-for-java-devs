"""Spec for ex02 (ilike search) — postgres-marked, skips without a DB."""

import pytest
from ex10_search import SearchTaskRepository
from persistapp.schemas import TaskCreate
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.postgres


@pytest.fixture
def repo(session: AsyncSession) -> SearchTaskRepository:
    return SearchTaskRepository(session)


async def test_search_matches_case_insensitively(repo: SearchTaskRepository) -> None:
    await repo.create(TaskCreate(title="Fix login"))
    await repo.create(TaskCreate(title="fix docs"))
    await repo.create(TaskCreate(title="Ship release"))
    results = await repo.search_title("fix")
    assert [t.title for t in results] == ["Fix login", "fix docs"]


async def test_search_with_uppercase_query(repo: SearchTaskRepository) -> None:
    await repo.create(TaskCreate(title="Fix login"))
    results = await repo.search_title("FIX")
    assert [t.title for t in results] == ["Fix login"]


async def test_search_without_match_returns_empty(repo: SearchTaskRepository) -> None:
    await repo.create(TaskCreate(title="ordinary"))
    assert list(await repo.search_title("zzz")) == []
