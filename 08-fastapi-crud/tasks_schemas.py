"""Pydantic v2 schemas ≈ DTOs + Bean Validation (@NotNull, @Size, ...).

Three separate models on purpose (see README "Why three schemas"):
- TaskCreate:   what the client may SEND on create (no id — the server assigns it)
- TaskUpdate:   partial update, every field optional (≈ a PATCH DTO)
- TaskResponse: what the server RETURNS (includes the server-managed id)

Run the API:  uv run uvicorn tasks_app:app --reload   (from 08-fastapi-crud/)
Swagger UI:   http://127.0.0.1:8000/docs
"""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    # extra="forbid" ≈ rejecting unknown JSON properties: a client sending
    # {"title": "x", "admin": true} gets a 422 instead of silently ignoring it.
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = False


class TaskUpdate(BaseModel):
    """PATCH semantics: only the fields the client sent get applied.

    `model_dump(exclude_unset=True)` on the store side distinguishes
    "field absent" from "field explicitly null" — Jackson can't do that.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None


class TaskResponse(BaseModel):
    """The public contract. If the internal model later grows fields
    (owner_id, created_at, ...), they do NOT leak unless added here."""

    id: int
    title: str
    description: str | None
    completed: bool
