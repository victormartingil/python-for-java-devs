"""Business logic ≈ @Service / use cases. Framework-free by construction.

Golden rule 3: NO FastAPI and NO SQLAlchemy imports in this file. It speaks
DTOs (schemas), domain records, and domain exceptions — so it is testable
with plain pytest, no app, no database (see tests/test_task_service.py).

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from collections.abc import Sequence

from app.core.exceptions import NotFoundError
from app.tasks.repository import TaskRepository
from app.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    """Depends on the TaskRepository PROTOCOL — duck typing means any object
    with the right methods works: Postgres today, in-memory in tests."""

    def __init__(self, tasks: TaskRepository) -> None:
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
            raise NotFoundError(f"task {task_id} not found")  # -> 404 via core/exceptions.py
        return TaskResponse.model_validate(record)

    async def update(self, task_id: int, data: TaskUpdate) -> TaskResponse:
        record = await self._tasks.update(task_id, data)
        if record is None:
            raise NotFoundError(f"task {task_id} not found")
        return TaskResponse.model_validate(record)

    async def delete(self, task_id: int) -> None:
        if not await self._tasks.delete(task_id):
            raise NotFoundError(f"task {task_id} not found")
