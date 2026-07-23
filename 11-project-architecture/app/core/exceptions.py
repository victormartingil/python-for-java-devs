"""Domain exceptions + global handlers ≈ business exceptions + @ControllerAdvice.

Services raise these; the HTTP mapping lives in exactly one place, so
service.py never imports FastAPI.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for business-rule violations (≈ your DomainException)."""


class NotFoundError(DomainError):
    pass


class UsernameTakenError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})

    @app.exception_handler(UsernameTakenError)
    async def username_taken_handler(request: Request, exc: UsernameTakenError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Incorrect username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
