"""The production app ≈ the same Spring Boot jar started with -Dspring.profiles.active=prod.

Module 11's create_app() is reused UNMODIFIED — production concerns are
added around it, not by editing it:

  1. structlog JSON logging (logging_config.py) — replaces the dev basicConfig
  2. a request-logging middleware (≈ a servlet filter / access log with context)
  3. the BackgroundTasks demo router (jobs.py)

/health comes from module 11's app — the Actuator-style liveness endpoint
the Docker HEALTHCHECK and your load balancer poll.

Run locally:   uv run uvicorn prodapp.main:app --port 8000
               (from 14-production-docker-ci/, with 11-project-architecture on PYTHONPATH —
               see tests/conftest.py; the Dockerfile sets this up for real)
Run for real:  docker compose up --build   (from 14-production-docker-ci/)
"""

from collections.abc import Awaitable, Callable

import structlog
from app.main import create_app  # module 11 — on PYTHONPATH, unmodified
from fastapi import FastAPI, Request, Response

from prodapp.jobs import router as jobs_router
from prodapp.logging_config import configure_structlog

request_log = structlog.get_logger("http")


def create_production_app() -> FastAPI:
    configure_structlog()
    app = create_app()  # registers exception handlers, users/tasks routers, /health

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # ≈ an access log that structured logging makes queryable:
        # path + status + method as FIELDS, not a string to regex.
        response = await call_next(request)
        request_log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )
        return response

    app.include_router(jobs_router)
    return app


app = create_production_app()
