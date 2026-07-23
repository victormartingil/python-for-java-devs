"""SOLUTION 11-01 (service) — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Sequence

from ex11_repository import InMemoryTaskRepository
from ex11_schemas import TaskCreate, TaskResponse, TaskUpdate


class NotFoundError(Exception):
    """Domain error -> 404 (module 11 keeps these in app/core/exceptions.py)."""


class TaskService:
    """Depends on the repository — duck typing means any object with the
    right methods works (Postgres adapter today, in-memory fake in tests)."""

    def __init__(self, tasks: InMemoryTaskRepository) -> None:
        self._tasks = tasks

    async def create(self, data: TaskCreate) -> TaskResponse:
        record = await self._tasks.create(data)
        return TaskResponse.model_validate(record)

    async def list(self, completed: bool | None = None) -> Sequence[TaskResponse]:
        records = await self._tasks.list(completed=completed)
        return [TaskResponse.model_validate(record) for record in records]

    async def get(self, task_id: int) -> TaskResponse:
        record = await self._tasks.get(task_id)
        if record is None:
            raise NotFoundError(f"task {task_id} not found")
        return TaskResponse.model_validate(record)

    async def update(self, task_id: int, data: TaskUpdate) -> TaskResponse:
        record = await self._tasks.update(task_id, data)
        if record is None:
            raise NotFoundError(f"task {task_id} not found")
        return TaskResponse.model_validate(record)

    async def delete(self, task_id: int) -> None:
        if not await self._tasks.delete(task_id):
            raise NotFoundError(f"task {task_id} not found")

    async def list_by_priority(self, priority: str) -> Sequence[TaskResponse]:
        records = await self._tasks.list()
        return [TaskResponse.model_validate(r) for r in records if r.priority == priority]
