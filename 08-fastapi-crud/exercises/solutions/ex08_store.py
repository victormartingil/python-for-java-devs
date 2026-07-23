"""SOLUTION 08-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from ex08_schemas import TaskCreate, TaskResponse, TaskUpdate


class TaskNotFoundError(Exception):
    """≈ EntityNotFoundException. The router translates it to a 404."""


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, TaskResponse] = {}
        self._next_id: int = 1

    def create(self, data: TaskCreate) -> TaskResponse:
        task = TaskResponse(id=self._next_id, **data.model_dump())
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def search(self, q: str) -> list[TaskResponse]:
        needle = q.lower()
        return [t for t in self._tasks.values() if needle in t.title.lower()]

    def list(self, *, completed: bool | None = None) -> list[TaskResponse]:
        tasks = list(self._tasks.values())
        if completed is not None:
            tasks = [t for t in tasks if t.completed is completed]
        return tasks

    def get(self, task_id: int) -> TaskResponse:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(f"task {task_id} not found") from None

    def update(self, task_id: int, data: TaskUpdate) -> TaskResponse:
        current = self.get(task_id)  # raises if missing
        updated = current.model_copy(update=data.model_dump(exclude_unset=True))
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> None:
        self.get(task_id)  # raises if missing
        del self._tasks[task_id]
