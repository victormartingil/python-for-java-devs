"""Exercise 09-03 — a global exception handler for a new domain error.

RateLimitError (given) is a domain error. demo_router (given) has an endpoint
that always raises it. Write register_rate_limit_handler: map the error to a
429 with a JSON detail — the @ControllerAdvice pattern: one place, no
try/except in endpoints. The tests are the spec:

    uv run pytest 09-fastapi-pro-di-auth-config/exercises -v

Hint: see 09-fastapi-pro-di-auth-config/secureapp/errors.py.
"""

from fastapi import APIRouter, FastAPI


class RateLimitError(Exception):
    """≈ a domain exception: the caller is asking too often."""


demo_router = APIRouter(tags=["demo"])


@demo_router.get("/demo/limited")
def demo_limited() -> None:
    """Always fails — provided so your handler has something to catch."""
    raise RateLimitError("demo quota exhausted")


def register_rate_limit_handler(app: FastAPI) -> None:
    """TODO(ex03): register an exception handler mapping RateLimitError to
    HTTP 429 with body {"detail": str(exc)}.

    @app.exception_handler(RateLimitError) decorates an async function
    (request, exc) -> JSONResponse. See secureapp/errors.py for the shape.
    """
    raise NotImplementedError("TODO(ex03): @app.exception_handler returning a 429 JSONResponse")
