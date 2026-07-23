"""In-memory storage for the exercise app — a copy of module 08's store.

EXERCISE 08-03 lives here: TaskStore.search.
The tests are the spec:

    uv run pytest 08-fastapi-crud/exercises -v
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
        """TODO(ex03): return all tasks whose TITLE contains q, case-insensitively.

        Java:    tasks.stream().filter(t -> t.getTitle().toLowerCase().contains(q.toLowerCase()))
        Python:  one comprehension — str.lower() and `in` (substring test ≈ String.contains).
        The router already wires GET /tasks?q=... to this method.

        (Declared before list() on purpose: a method named `list` shadows the
        builtin inside the class body, so list[...] annotations must come first.)
        """
        raise NotImplementedError("TODO(ex03): case-insensitive substring match on title")

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
