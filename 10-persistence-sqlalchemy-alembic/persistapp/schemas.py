"""Pydantic schemas — same contract as modules 08–09.

New in this module: `from_attributes=True` on TaskResponse lets FastAPI build
it straight from ORM objects (response_model serializes through the schema —
the ORM entity itself is never exposed). Module 11 tightens this further by
converting explicitly in the service layer.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn persistapp.main:app --reload   (from 10-persistence-sqlalchemy-alembic/)
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
    # ≈ mapping an @Entity onto a DTO with ModelMapper/MapStruct, but declarative.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
