"""API integration tests against real PostgreSQL.

Marked `postgres`: they SKIP when no DB is reachable — see conftest.py.
Run them with:  docker compose up -d  &&  uv run pytest -m postgres

Why AsyncClient + ASGITransport instead of TestClient: the asyncpg connection
is bound to the test's event loop, and TestClient runs the app on a different
one. AsyncClient(ASGITransport(app)) executes requests IN the current loop,
so the overridden session dependency works. (First taste of
app.dependency_overrides ≈ @MockBean — module 11 makes it the star.)
"""

from collections.abc import AsyncIterator

import pytest
from httpx2 import ASGITransport, AsyncClient
from persistapp.database import get_session
from persistapp.main import app
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.postgres


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """The real app, but its session dependency swapped for the test's (clean) session."""
    app.dependency_overrides[get_session] = lambda: session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


async def test_full_crud_flow(client: AsyncClient) -> None:
    created = await client.post("/tasks", json={"title": "db-backed task"})
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert task_id == 1  # table was truncated: deterministic ids

    fetched = await client.get(f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "db-backed task"
    assert "hashed" not in fetched.text  # response_model is the contract

    updated = await client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    listed = await client.get("/tasks", params={"completed": True})
    assert task_id in [t["id"] for t in listed.json()]

    assert (await client.delete(f"/tasks/{task_id}")).status_code == 204
    assert (await client.get(f"/tasks/{task_id}")).status_code == 404


async def test_get_missing_returns_404(client: AsyncClient) -> None:
    assert (await client.get("/tasks/999")).status_code == 404


async def test_validation_error_returns_422(client: AsyncClient) -> None:
    assert (await client.post("/tasks", json={"title": ""})).status_code == 422
