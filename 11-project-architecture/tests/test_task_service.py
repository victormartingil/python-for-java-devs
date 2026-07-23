"""Pure service tests: no FastAPI, no database, no event loop plumbing.

The service only knows the TaskRepository protocol, so the in-memory fake
slots straight in. This is the bulk of the test pyramid (≈ plain JUnit tests
of a @Service with a stubbed repository). Async methods need pytest-asyncio
(already configured repo-wide with asyncio_mode = "auto").
"""

import pytest
from app.core.exceptions import NotFoundError
from app.tasks.repository import InMemoryTaskRepository
from app.tasks.schemas import TaskCreate, TaskUpdate
from app.tasks.service import TaskService


@pytest.fixture
def service() -> TaskService:
    return TaskService(InMemoryTaskRepository())


async def test_create_and_get(service: TaskService) -> None:
    created = await service.create(TaskCreate(title="domain logic", description="pure python"))
    assert created.id == 1
    fetched = await service.get(created.id)
    assert fetched.title == "domain logic"
    assert fetched.completed is False


async def test_list_filter(service: TaskService) -> None:
    await service.create(TaskCreate(title="a"))
    await service.create(TaskCreate(title="b", completed=True))
    assert [t.title for t in await service.list()] == ["a", "b"]
    assert [t.title for t in await service.list(completed=True)] == ["b"]


async def test_update_applies_only_sent_fields(service: TaskService) -> None:
    created = await service.create(TaskCreate(title="keep", description="also keep"))
    updated = await service.update(created.id, TaskUpdate(completed=True))
    assert updated.completed is True
    assert updated.title == "keep"
    assert updated.description == "also keep"


async def test_get_missing_raises_not_found(service: TaskService) -> None:
    with pytest.raises(NotFoundError):
        await service.get(999)


async def test_update_missing_raises_not_found(service: TaskService) -> None:
    with pytest.raises(NotFoundError):
        await service.update(999, TaskUpdate(completed=True))


async def test_delete_then_get_raises(service: TaskService) -> None:
    created = await service.create(TaskCreate(title="gone"))
    await service.delete(created.id)
    with pytest.raises(NotFoundError):
        await service.get(created.id)
    with pytest.raises(NotFoundError):
        await service.delete(created.id)
