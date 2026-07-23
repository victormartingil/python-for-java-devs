"""HTTP middleware ≈ a servlet Filter (OncePerRequestFilter).

Wraps every request/response — use it for cross-cutting concerns: timing,
logging, correlation ids. AuthZ/AuthN is usually better expressed as a
dependency (get_current_user), not middleware, so it shows up in OpenAPI.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response


def register_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_process_time_header(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)  # ≈ filterChain.doFilter(request, response)
        response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
        return response
