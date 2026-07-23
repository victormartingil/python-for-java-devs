"""Put the module root on sys.path so `import secureapp` works,
plus shared fixtures: an in-process client and a registered-and-logged-in user.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:  # gated deps (web group) — the root conftest skips this dir when absent
    from fastapi.testclient import TestClient
    from secureapp.main import app  # noqa: E402  (import after sys.path wiring)
except ModuleNotFoundError:  # light `uv sync` profile — tests never run here
    TestClient = None  # type: ignore[assignment]
    app = None

GOOD_PASSWORD = "supersecret1"


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def username() -> str:
    """Unique per test — the in-memory user store is a process singleton."""
    return f"user_{uuid4().hex[:10]}"


@pytest.fixture
def auth_headers(client: TestClient, username: str) -> dict[str, str]:
    """Register + login, return the Authorization header (≈ a test security context)."""
    response = client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    assert response.status_code == 201
    token = client.post(
        "/auth/token", data={"username": username, "password": GOOD_PASSWORD}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
