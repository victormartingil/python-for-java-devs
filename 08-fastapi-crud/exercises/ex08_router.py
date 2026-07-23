"""APIRouter for the exercise app — a copy of module 08's router.

EXERCISE 08-01 lives here: GET /tasks/stats.
The tests are the spec:

    uv run pytest 08-fastapi-crud/exercises -v
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
    # GET /tasks?q=fix -> store.search(q)  (exercise 08-03: the store method is yours)
    if q is not None:
        return store.search(q)
    return store.list(completed=completed)


@router.get("/stats", response_model=TaskStats)
def task_stats() -> TaskStats:
    """TODO(ex01): return TaskStats(total=..., completed=..., pending=...).

    - total     = number of tasks
    - completed = how many are done
    - pending   = the rest

    Compute from store.list() with a generator expression + sum().
    Route-order note: /stats is declared BEFORE /{task_id} on purpose —
    first match wins (≈ specific ant patterns before generic ones in Spring).
    """
    raise NotImplementedError("TODO(ex01): count from store.list() and return TaskStats")


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
