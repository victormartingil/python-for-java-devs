"""SOLUTION 11-01 (repository) — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ex11_schemas import TaskCreate, TaskUpdate


@dataclass
class TaskRecord:
    """What the domain layer sees — a plain value object, not an ORM entity."""

    id: int
    title: str
    description: str | None
    completed: bool
    priority: str


class InMemoryTaskRepository:
    """The in-memory adapter — same shape as module 11's, zero I/O."""

    def __init__(self) -> None:
        self._rows: dict[int, TaskRecord] = {}
        self._next_id: int = 1

    async def create(self, data: TaskCreate) -> TaskRecord:
        record = TaskRecord(id=self._next_id, **data.model_dump())
        self._rows[record.id] = record
        self._next_id += 1
        return record

    async def list(self, completed: bool | None = None) -> Sequence[TaskRecord]:
        records = list(self._rows.values())
        if completed is not None:
            records = [r for r in records if r.completed is completed]
        return records

    async def get(self, task_id: int) -> TaskRecord | None:
        return self._rows.get(task_id)

    async def update(self, task_id: int, data: TaskUpdate) -> TaskRecord | None:
        record = self._rows.get(task_id)
        if record is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        return record

    async def delete(self, task_id: int) -> bool:
        return self._rows.pop(task_id, None) is not None
