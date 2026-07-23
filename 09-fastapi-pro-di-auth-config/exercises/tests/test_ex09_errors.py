"""Spec for ex03 (429 handler) — make these pass."""

from ex09_errors import demo_router, register_rate_limit_handler
from fastapi import FastAPI
from fastapi.testclient import TestClient


def build_client() -> TestClient:
    app = FastAPI()
    register_rate_limit_handler(app)  # raises NotImplementedError until you implement it
    app.include_router(demo_router)
    return TestClient(app)


def test_rate_limit_error_maps_to_429() -> None:
    response = build_client().get("/demo/limited")
    assert response.status_code == 429, "register a handler for RateLimitError in ex09_errors.py"


def test_rate_limit_response_carries_the_detail() -> None:
    assert build_client().get("/demo/limited").json() == {"detail": "demo quota exhausted"}
