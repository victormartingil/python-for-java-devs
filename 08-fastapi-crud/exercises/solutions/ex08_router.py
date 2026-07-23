"""SOLUTION 08-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from ex08_schemas import TaskCreate, TaskResponse, TaskStats, TaskUpdate
from ex08_store import TaskNotFoundError, TaskStore
from fastapi import APIRouter, HTTPException, Response, status

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Module-level singleton: fine for an in-memory exercise app (same as module 08).
store = TaskStore()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> TaskResponse:
    return store.create(data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(completed: bool | None = None, q: str | None = None) -> list[TaskResponse]:
    if q is not None:
        return store.search(q)
    return store.list(completed=completed)


@router.get("/stats", response_model=TaskStats)
def task_stats() -> TaskStats:
    tasks = store.list()
    completed = sum(1 for task in tasks if task.completed)
    return TaskStats(total=len(tasks), completed=completed, pending=len(tasks) - completed)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> TaskResponse:
    try:
        return store.get(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from exc


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate) -> TaskResponse:
    try:
        return store.update(task_id, data)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from exc


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    try:
        store.delete(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
