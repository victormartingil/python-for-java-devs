"""Exercise 11-01 (flagship) — layer 1: schemas.

You are adding a `priority` field to the tasks feature across ALL layers:
schemas -> record -> service -> router. This file is the contract layer.

    uv run pytest 11-project-architecture/exercises -v

TODO(ex01) — three small additions (import Literal from typing first):
- TaskCreate:   `priority: Literal["low", "medium", "high"] = "medium"`
                The default IS the business rule "medium unless told
                otherwise", expressed as a schema default.
- TaskUpdate:   `priority: Literal["low", "medium", "high"] | None = None`
- TaskResponse: `priority: str`

Hint: mirror the existing Field declarations; see
11-project-architecture/app/tasks/schemas.py.
"""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False
    # TODO(ex01): priority — Literal["low", "medium", "high"], default "medium"


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None
    # TODO(ex01): priority — same Literal, optional, default None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    # TODO(ex01): priority: str
