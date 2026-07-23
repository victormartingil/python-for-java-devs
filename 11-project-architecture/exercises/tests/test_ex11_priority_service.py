"""Service-level spec for the priority feature — no FastAPI, no database."""

import pytest
from ex11_repository import InMemoryTaskRepository
from ex11_schemas import TaskCreate
from ex11_service import TaskService
from pydantic import ValidationError


@pytest.fixture
def service() -> TaskService:
    return TaskService(InMemoryTaskRepository())


async def test_priority_defaults_to_medium(service: TaskService) -> None:
    created = await service.create(TaskCreate(title="no priority given"))
    assert created.priority == "medium", "add priority to TaskCreate with default 'medium'"


async def test_explicit_priority_is_kept(service: TaskService) -> None:
    created = await service.create(TaskCreate(title="urgent thing", priority="high"))
    assert created.priority == "high"


async def test_invalid_priority_is_rejected_by_the_schema() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title="x", priority="urgent")


async def test_list_by_priority_filters(service: TaskService) -> None:
    await service.create(TaskCreate(title="a", priority="high"))
    await service.create(TaskCreate(title="b"))  # medium
    await service.create(TaskCreate(title="c", priority="high"))
    assert [t.title for t in await service.list_by_priority("high")] == ["a", "c"]
    assert [t.title for t in await service.list_by_priority("low")] == []
