"""Pydantic v2 schemas for the exercise app — a copy of module 08's.

EXERCISE 08-02 lives here: add a validation rule to TaskCreate.
The tests are the spec:

    uv run pytest 08-fastapi-crud/exercises -v

Hint: see the Field(...) constraints below and 08-fastapi-crud/tasks_schemas.py.
A field_validator runs per field; raising ValueError inside it becomes a 422
(≈ a Bean Validation ConstraintValidator).
"""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """TODO(ex02): titles are messy user input — normalize and reject:

    - strip leading/trailing whitespace ("  padded  " -> "padded")
    - reject titles that are EMPTY after stripping ("   " -> 422)

    Add a field_validator("title") doing both: import field_validator from
    pydantic, decorate a @classmethod taking (cls, value: str) -> str, return
    the cleaned value or raise ValueError with a helpful message.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class TaskUpdate(BaseModel):
    """PATCH semantics: only the fields the client sent get applied."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None


class TaskResponse(BaseModel):
    """The public contract — internal details never leak."""

    id: int
    title: str
    description: str | None
    completed: bool


class TaskStats(BaseModel):
    """The contract for EXERCISE 08-01 — your /tasks/stats endpoint returns this."""

    total: int
    completed: int
    pending: int
