"""Exercise 10-01 — extend the repository: count + pagination.

ExtendedTaskRepository inherits module 10's TaskRepository; you add the two
query methods a real API needs. The tests run against REAL PostgreSQL (marked
`postgres` — they skip when no DB is reachable):

    cd 10-persistence-sqlalchemy-alembic && docker compose up -d
    uv run pytest 10-persistence-sqlalchemy-alembic/exercises -v

Hint: see persistapp/repository.py — select() reads like JPQL but it's typed
Python. For counting: select(func.count()).select_from(TaskModel); you'll need
`from sqlalchemy import func, select` and `from persistapp.models import TaskModel`.
"""

from collections.abc import Sequence

from persistapp.models import TaskModel
from persistapp.repository import TaskRepository


class ExtendedTaskRepository(TaskRepository):
    """Module 10's repository plus the methods you're implementing."""

    async def count(self, completed: bool | None = None) -> int:
        """TODO(ex01): COUNT tasks, optionally filtered by `completed`.

        ≈ Spring Data's `long countByCompleted(boolean completed)`.
        func.count() ≈ COUNT(*) — execute the statement, take scalar_one().
        Mirror list()'s pattern: build the statement, add .where(...) only
        when completed is not None.
        """
        raise NotImplementedError("TODO(ex01): select(func.count()) with an optional where")

    async def list_page(self, *, limit: int, offset: int = 0) -> Sequence[TaskModel]:
        """TODO(ex01): a page of tasks, ordered by id.

        ≈ Pageable/Page in Spring Data. .limit(...) and .offset(...) on the
        select — always with order_by, or pages come back nondeterministic.
        """
        raise NotImplementedError("TODO(ex01): order_by(id).limit(...).offset(...)")
