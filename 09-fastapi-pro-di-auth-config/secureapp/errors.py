"""Domain errors + global handlers ≈ custom exceptions + @ControllerAdvice.

Compare with module 08, where every endpoint had try/except → HTTPException.
Here endpoints just let domain exceptions bubble up, and ONE place maps them
to HTTP responses — exactly like @ExceptionHandler methods in Spring.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class TaskNotFoundError(Exception):
    pass


class UsernameTakenError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(UsernameTakenError)
    async def username_taken_handler(request: Request, exc: UsernameTakenError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})
