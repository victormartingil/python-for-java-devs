"""APIRouter ≈ @RestController: a group of endpoints under a common prefix.

Read the decorators as Spring annotations:
    @router.post("", status_code=201)     ≈ @PostMapping + @ResponseStatus(CREATED)
    task_id: int (in the path)            ≈ @PathVariable
    completed: bool | None = None         ≈ @RequestParam(required = false)
    data: TaskCreate (a Pydantic model)   ≈ @RequestBody @Valid

Run the API:  uv run uvicorn tasks_app:app --reload   (from 08-fastapi-crud/)
Swagger UI:   http://127.0.0.1:8000/docs
"""

from fastapi import APIRouter, HTTPException, Response, status
from tasks_schemas import TaskCreate, TaskResponse, TaskUpdate
from tasks_store import TaskNotFoundError, TaskStore

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Module-level singleton: fine for an in-memory demo. Module 09 replaces this
# with dependency injection (Depends), which is what you'd do in real code.
store = TaskStore()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> TaskResponse:
    # FastAPI has already validated the JSON body against TaskCreate.
    # Invalid payloads never reach this line — they get an automatic 422.
    return store.create(data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(completed: bool | None = None) -> list[TaskResponse]:
    # GET /tasks            -> all tasks
    # GET /tasks?completed=true -> filtered (query param parsed + validated as bool)
    return store.list(completed=completed)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int) -> TaskResponse:
    try:
        return store.get(task_id)
    except TaskNotFoundError as exc:
        # Raising HTTPException ≈ throwing a ResponseStatusException.
        # (Module 09 shows the cleaner global-handler version ≈ @ControllerAdvice.)
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
