"""Repository ≈ a Spring Data repository, written explicitly.

`select()` is the 2.0 query API — reads like JPQL but it's typed Python:
    select(TaskModel).where(TaskModel.completed.is_(True)).order_by(TaskModel.id)

Methods return ORM models (or None — no Optional<Task> wrapper ceremony,
`TaskModel | None` is the Python `Optional<TaskModel>`).

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from persistapp.models import TaskModel
from persistapp.schemas import TaskCreate, TaskUpdate


class TaskRepository:
    """One per request, built around the request's AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: TaskCreate) -> TaskModel:
        task = TaskModel(**data.model_dump())
        self._session.add(task)  # ≈ em.persist() — INSERT happens on flush
        await self._session.flush()  # flush ≈ em.flush(): get the generated id now
        await self._session.refresh(task)
        return task

    async def list(self, completed: bool | None = None) -> Sequence[TaskModel]:
        statement = select(TaskModel).order_by(TaskModel.id)
        if completed is not None:
            statement = statement.where(TaskModel.completed.is_(completed))
        result = await self._session.execute(statement)
        return result.scalars().all()

    async def get(self, task_id: int) -> TaskModel | None:
        return await self._session.get(TaskModel, task_id)  # ≈ em.find() — by PK

    async def update(self, task: TaskModel, data: TaskUpdate) -> TaskModel:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)  # dirty checking ≈ Hibernate's, on flush
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def delete(self, task: TaskModel) -> None:
        await self._session.delete(task)  # ≈ em.remove()
        await self._session.flush()
