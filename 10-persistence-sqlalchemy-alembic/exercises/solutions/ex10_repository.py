"""SOLUTION 10-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Sequence

from persistapp.models import TaskModel
from persistapp.repository import TaskRepository
from sqlalchemy import func, select


class ExtendedTaskRepository(TaskRepository):
    """Module 10's repository plus the methods you're implementing."""

    async def count(self, completed: bool | None = None) -> int:
        statement = select(func.count()).select_from(TaskModel)
        if completed is not None:
            statement = statement.where(TaskModel.completed.is_(completed))
        result = await self._session.execute(statement)
        return result.scalar_one()

    async def list_page(self, *, limit: int, offset: int = 0) -> Sequence[TaskModel]:
        statement = select(TaskModel).order_by(TaskModel.id).limit(limit).offset(offset)
        result = await self._session.execute(statement)
        return result.scalars().all()
