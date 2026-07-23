"""SOLUTION 08-02 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title must not be blank")
        return cleaned


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
