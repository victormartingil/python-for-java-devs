"""HTTP layer ≈ @RestController. Golden rule 1: THIN.

Parse the request, call the service, return the response. Zero business
logic, zero SQL, zero session handling — the wiring comes from dependencies.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUserDep, TaskServiceDep
from app.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate

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
