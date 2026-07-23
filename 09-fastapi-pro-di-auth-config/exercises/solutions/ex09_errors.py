"""SOLUTION 09-03 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse


class RateLimitError(Exception):
    """≈ a domain exception: the caller is asking too often."""


demo_router = APIRouter(tags=["demo"])


@demo_router.get("/demo/limited")
def demo_limited() -> None:
    """Always fails — provided so your handler has something to catch."""
    raise RateLimitError("demo quota exhausted")


def register_rate_limit_handler(app: FastAPI) -> None:
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": str(exc)}
        )
