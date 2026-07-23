"""Pydantic DTOs ≈ request/response records + Bean Validation.

Golden rule 2: schemas are NOT the ORM model. The HTTP contract is defined
here and only here; TaskModel could gain columns tomorrow without leaking.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None


class TaskResponse(BaseModel):
    # from_attributes lets the service build it from a TaskRecord dataclass.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
