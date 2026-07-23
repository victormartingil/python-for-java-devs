"""Exercise 10-02 — a case-insensitive substring search with ilike.

SearchTaskRepository adds title search to module 10's TaskRepository.
Tests are postgres-marked (they skip when no DB is reachable):

    cd 10-persistence-sqlalchemy-alembic && docker compose up -d
    uv run pytest 10-persistence-sqlalchemy-alembic/exercises -v

Hint: column.ilike(f"%{q}%") ≈ LOWER(title) LIKE LOWER('%q%'); you'll need
`from sqlalchemy import select` (TaskModel is already imported below).
"""

from collections.abc import Sequence

from persistapp.models import TaskModel
from persistapp.repository import TaskRepository


class SearchTaskRepository(TaskRepository):
    """Module 10's repository plus title search."""

    async def search_title(self, q: str) -> Sequence[TaskModel]:
        """TODO(ex02): tasks whose title contains q, case-insensitively,
        ordered by id. ≈ the derived query findByTitleContainingIgnoreCase.
        """
        raise NotImplementedError("TODO(ex02): where(TaskModel.title.ilike(f'%{q}%'))")
