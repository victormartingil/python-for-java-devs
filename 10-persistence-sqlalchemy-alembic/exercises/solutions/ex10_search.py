"""SOLUTION 10-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Sequence

from persistapp.models import TaskModel
from persistapp.repository import TaskRepository
from sqlalchemy import select


class SearchTaskRepository(TaskRepository):
    """Module 10's repository plus title search."""

    async def search_title(self, q: str) -> Sequence[TaskModel]:
        statement = select(TaskModel).where(TaskModel.title.ilike(f"%{q}%")).order_by(TaskModel.id)
        result = await self._session.execute(statement)
        return result.scalars().all()
