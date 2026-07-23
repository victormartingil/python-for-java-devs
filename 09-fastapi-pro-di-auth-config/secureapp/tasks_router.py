"""Tasks endpoints — module 08's CRUD, now protected and DI-wired.

Every endpoint declares `current_user: CurrentUserDep`, so all of /tasks
requires a valid JWT (≈ a secured @RestController with an Authentication
parameter). Compare with module 08: no try/except for 404s anymore — the
global handler in errors.py does it (≈ @ControllerAdvice).

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from fastapi import APIRouter, Response, status

from secureapp.dependencies import CurrentUserDep, TaskStoreDep
from secureapp.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate, store: TaskStoreDep, current_user: CurrentUserDep
) -> TaskResponse:
    return store.create(data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    store: TaskStoreDep, current_user: CurrentUserDep, completed: bool | None = None
) -> list[TaskResponse]:
    return store.list(completed=completed)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, store: TaskStoreDep, current_user: CurrentUserDep) -> TaskResponse:
    return store.get(task_id)  # TaskNotFoundError -> 404 via the global handler


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, data: TaskUpdate, store: TaskStoreDep, current_user: CurrentUserDep
) -> TaskResponse:
    return store.update(task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, store: TaskStoreDep, current_user: CurrentUserDep) -> Response:
    store.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
