"""Tasks endpoints — same HTTP contract as module 08, now over PostgreSQL.

Everything is `async def` because the session does real async I/O (asyncpg).
The dependency chain: endpoint -> TaskRepository -> AsyncSession (per request).

Honest typing note: endpoints return ORM models (TaskModel); the declared
`response_model=TaskResponse` serializes them through the public schema, so the
entity's shape is never the API contract. Module 11 moves the conversion into
a service layer, where it belongs in bigger apps.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
"""

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from persistapp.database import get_session
from persistapp.models import TaskModel
from persistapp.repository import TaskRepository
from persistapp.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> TaskRepository:
    """A small DI factory — the pattern module 11 generalizes."""
    return TaskRepository(session)


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repository)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, repo: TaskRepoDep) -> TaskModel:
    return await repo.create(data)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(repo: TaskRepoDep, completed: bool | None = None) -> Sequence[TaskModel]:
    return await repo.list(completed=completed)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, repo: TaskRepoDep) -> TaskModel:
    task = await repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, data: TaskUpdate, repo: TaskRepoDep) -> TaskModel:
    task = await repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await repo.update(task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, repo: TaskRepoDep) -> Response:
    task = await repo.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await repo.delete(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
