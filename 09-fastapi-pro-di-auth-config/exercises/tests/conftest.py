"""Exercise-test wiring: stubs importable + the module's secureapp package,
plus shared fixtures: a mini app (real auth router + the exercise router)
and a registered-and-logged-in user.
"""

import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # exercises/ (the stubs)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # module root (secureapp)

from ex09_router import router as me_router  # noqa: E402  (import after sys.path wiring)
from secureapp.auth_router import router as auth_router  # noqa: E402

GOOD_PASSWORD = "supersecret1"


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(me_router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Register + login with a unique user, return the Authorization header."""
    username = f"user_{uuid4().hex[:10]}"
    response = client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    assert response.status_code == 201
    token = client.post(
        "/auth/token", data={"username": username, "password": GOOD_PASSWORD}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
