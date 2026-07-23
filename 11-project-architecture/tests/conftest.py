"""Test wiring for module 11 — the @MockBean moment.

The API tests run the REAL app (real routers, real services, real auth),
but with the repositories swapped for in-memory fakes via
`app.dependency_overrides` — no database, no mocks of business logic,
full HTTP behavior. The services and domain are completely untouched.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:  # gated deps (web group) — the root conftest skips this dir when absent
    from app.dependencies import get_task_repository, get_user_repository  # noqa: E402
    from app.main import app  # noqa: E402
    from app.tasks.repository import InMemoryTaskRepository  # noqa: E402
    from app.users.repository import InMemoryUserRepository  # noqa: E402
    from fastapi.testclient import TestClient
except ModuleNotFoundError:  # light `uv sync` profile — tests never run here
    TestClient = None  # type: ignore[assignment]

GOOD_PASSWORD = "supersecret1"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """The production app, wired to in-memory repositories.

    app.dependency_overrides[get_task_repository] ≈ replacing the @Bean for
    the scope of the test. One instance per fixture, shared across requests
    (a lambda returning a NEW repo per request would lose state).
    """
    task_repo = InMemoryTaskRepository()
    user_repo = InMemoryUserRepository()
    app.dependency_overrides[get_task_repository] = lambda: task_repo
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/register", json={"username": "alice", "password": GOOD_PASSWORD})
    assert response.status_code == 201
    token = client.post(
        "/auth/token", data={"username": "alice", "password": GOOD_PASSWORD}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
