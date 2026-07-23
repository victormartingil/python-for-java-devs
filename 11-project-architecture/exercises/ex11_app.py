"""The exercise app (provided) — module 11's architecture, DB-free.

Layers: router -> service -> repository, wired in ex11_dependencies.py.
NotFoundError maps to 404 in exactly one place (≈ @ControllerAdvice).

    uv run pytest 11-project-architecture/exercises -v
"""

from ex11_router import router as tasks_router
from ex11_service import NotFoundError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI(title="Module 11 exercises — the priority feature", version="0.11.1")


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


app.include_router(tasks_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
