"""Exercise 11-01 (flagship) — layer 3: service.

Framework-free business logic (golden rule: no FastAPI/SQLAlchemy imports in
this file). Most of TaskService is given — you add the priority behavior.

    uv run pytest 11-project-architecture/exercises -v

Hint: 11-project-architecture/app/tasks/service.py.
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
        """TODO(ex01): return the tasks with the given priority.

        Filter from self._tasks.list() and convert to TaskResponse the same
        way list() does. (A bigger system might push this into the query;
        the point here is layer discipline: router -> service -> repository.)
        """
        raise NotImplementedError("TODO(ex01): filter tasks by priority, convert to TaskResponse")
