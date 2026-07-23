"""Exercise 11-01 (flagship) — layer 4: router. Golden rule: THIN.

Given, except one endpoint: GET /tasks/by-priority/{priority}.

    uv run pytest 11-project-architecture/exercises -v

Hint: 11-project-architecture/app/tasks/router.py — parse, call service,
return. Route order matters: /by-priority/... is declared BEFORE /{task_id}
(first match wins ≈ specific ant patterns before generic ones in Spring).
"""

from ex11_dependencies import CurrentUserDep, TaskServiceDep
from ex11_schemas import TaskCreate, TaskResponse, TaskUpdate
from fastapi import APIRouter, Response, status

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskResponse:
    return await service.create(data)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    service: TaskServiceDep, current_user: CurrentUserDep, completed: bool | None = None
) -> list[TaskResponse]:
    return list(await service.list(completed=completed))


@router.get("/by-priority/{priority}", response_model=list[TaskResponse])
async def list_tasks_by_priority(
    priority: str, service: TaskServiceDep, current_user: CurrentUserDep
) -> list[TaskResponse]:
    """TODO(ex01): one line — delegate to the service and return a list."""
    raise NotImplementedError("TODO(ex01): return list(await service.list_by_priority(priority))")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskResponse:
    return await service.get(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, data: TaskUpdate, service: TaskServiceDep, current_user: CurrentUserDep
) -> TaskResponse:
    return await service.update(task_id, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, service: TaskServiceDep, current_user: CurrentUserDep
) -> Response:
    await service.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
