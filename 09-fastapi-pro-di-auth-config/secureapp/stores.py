"""In-memory stores — same role as module 08's TaskStore, now also for users.

Still a demo: module 10 replaces dicts with PostgreSQL. What matters here is
that routers never touch these directly — they receive them via Depends
(see dependencies.py), so the swap later touches zero endpoint code.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from dataclasses import dataclass

from secureapp.errors import TaskNotFoundError, UsernameTakenError
from secureapp.schemas import TaskCreate, TaskResponse, TaskUpdate


@dataclass
class UserRecord:
    """Internal user representation — NEVER serialized to clients
    (UserResponse in schemas.py is the public shape: no password hash)."""

    id: int
    username: str
    hashed_password: str


class UserStore:
    def __init__(self) -> None:
        self._users: dict[str, UserRecord] = {}
        self._next_id: int = 1

    def create(self, username: str, hashed_password: str) -> UserRecord:
        if username in self._users:
            raise UsernameTakenError(f"username '{username}' is already taken")
        user = UserRecord(id=self._next_id, username=username, hashed_password=hashed_password)
        self._users[username] = user
        self._next_id += 1
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        return self._users.get(username)


class TaskStore:
    """Identical logic to module 08's store."""

    def __init__(self) -> None:
        self._tasks: dict[int, TaskResponse] = {}
        self._next_id: int = 1

    def create(self, data: TaskCreate) -> TaskResponse:
        task = TaskResponse(id=self._next_id, **data.model_dump())
        self._tasks[task.id] = task
        self._next_id += 1
        return task

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
        current = self.get(task_id)
        updated = current.model_copy(update=data.model_dump(exclude_unset=True))
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> None:
        self.get(task_id)
        del self._tasks[task_id]


# Singletons — injected into endpoints with Depends (see dependencies.py).
user_store = UserStore()
task_store = TaskStore()
