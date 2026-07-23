"""Data access ≈ the Spring Data repository — plus the Python twist.

`TaskRepository` is a typing.Protocol: a STRUCTURAL contract (module 04).
No class inherits from it; SqlAlchemyTaskRepository and InMemoryTaskRepository
simply have the right shape, and mypy verifies it. That is the "port" in
ports & adapters — without a nominal interface hierarchy.

The repository boundary returns TaskRecord (a plain dataclass), never the
ORM model: above this line, SQLAlchemy does not exist.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.models import TaskModel
from app.tasks.schemas import TaskCreate, TaskUpdate


@dataclass
class TaskRecord:
    """What the domain layer sees — a plain value object, not an ORM entity."""

    id: int
    title: str
    description: str | None
    completed: bool


class TaskRepository(Protocol):
    """The contract the service depends on (≈ the repository port).

    Structural, not nominal: implementations don't declare `implements`."""

    async def create(self, data: TaskCreate) -> TaskRecord: ...
    async def list(self, completed: bool | None = None) -> Sequence[TaskRecord]: ...
    async def get(self, task_id: int) -> TaskRecord | None: ...
    async def update(self, task_id: int, data: TaskUpdate) -> TaskRecord | None: ...
    async def delete(self, task_id: int) -> bool: ...


def _to_record(task: TaskModel) -> TaskRecord:
    return TaskRecord(
        id=task.id, title=task.title, description=task.description, completed=task.completed
    )


class SqlAlchemyTaskRepository:
    """The Postgres adapter. One per request, around the request's session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: TaskCreate) -> TaskRecord:
        task = TaskModel(**data.model_dump())
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return _to_record(task)

    async def list(self, completed: bool | None = None) -> Sequence[TaskRecord]:
        statement = select(TaskModel).order_by(TaskModel.id)
        if completed is not None:
            statement = statement.where(TaskModel.completed.is_(completed))
        result = await self._session.execute(statement)
        return [_to_record(task) for task in result.scalars().all()]

    async def get(self, task_id: int) -> TaskRecord | None:
        task = await self._session.get(TaskModel, task_id)
        return _to_record(task) if task is not None else None

    async def update(self, task_id: int, data: TaskUpdate) -> TaskRecord | None:
        task = await self._session.get(TaskModel, task_id)
        if task is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        await self._session.flush()
        await self._session.refresh(task)
        return _to_record(task)

    async def delete(self, task_id: int) -> bool:
        task = await self._session.get(TaskModel, task_id)
        if task is None:
            return False
        await self._session.delete(task)
        await self._session.flush()
        return True


class InMemoryTaskRepository:
    """The test adapter — same shape, zero I/O (≈ a hand-written fake).

    Swapped in via app.dependency_overrides in tests — see tests/conftest.py.
    THIS is the ports & adapters benefit, achieved with duck typing + DI.
    """

    def __init__(self) -> None:
        self._rows: dict[int, TaskRecord] = {}
        self._next_id: int = 1

    async def create(self, data: TaskCreate) -> TaskRecord:
        record = TaskRecord(id=self._next_id, **data.model_dump())
        self._rows[record.id] = record
        self._next_id += 1
        return record

    async def list(self, completed: bool | None = None) -> Sequence[TaskRecord]:
        records = list(self._rows.values())
        if completed is not None:
            records = [r for r in records if r.completed is completed]
        return records

    async def get(self, task_id: int) -> TaskRecord | None:
        return self._rows.get(task_id)

    async def update(self, task_id: int, data: TaskUpdate) -> TaskRecord | None:
        record = self._rows.get(task_id)
        if record is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        return record

    async def delete(self, task_id: int) -> bool:
        return self._rows.pop(task_id, None) is not None
