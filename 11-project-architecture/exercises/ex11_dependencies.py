"""Exercise app wiring ≈ app/dependencies.py in module 11 (provided).

The composition root: a module-level in-memory repository behind a dependency,
so tests can swap it via app.dependency_overrides (≈ replacing the @Bean for
the scope of a test). get_current_user is a STAND-IN for the real JWT
dependency (modules 09/11) — it returns a fixed user; the point here is the
wiring pattern, not security.
"""

from dataclasses import dataclass
from typing import Annotated

from ex11_repository import InMemoryTaskRepository
from ex11_service import TaskService
from fastapi import Depends


@dataclass
class CurrentUser:
    id: int
    username: str


_task_repository = InMemoryTaskRepository()


def get_task_service() -> TaskService:
    """The swappable bean: tests override this to get FRESH state per test."""
    return TaskService(_task_repository)


async def get_current_user() -> CurrentUser:
    return CurrentUser(id=1, username="exercise-user")


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]
