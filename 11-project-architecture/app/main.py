"""Composition root ≈ the @SpringBootApplication class.

Creates the app, registers cross-cutting concerns and routers. Object wiring
lives in dependencies.py; this file is about the APPLICATION, not the beans.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
Swagger UI: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.tasks.router import router as tasks_router
from app.users.router import router as users_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Tasks API — module 11 (layered by domain)", version="0.11.0")
    register_exception_handlers(app)
    app.include_router(users_router)
    app.include_router(tasks_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
