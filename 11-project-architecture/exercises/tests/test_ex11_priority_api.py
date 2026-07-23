"""API-level spec for the priority feature — real app, repository swapped
via dependency_overrides: the module 11 test pattern (fresh state per test).
"""

from collections.abc import Iterator

import pytest
from ex11_app import app
from ex11_dependencies import get_task_service
from ex11_repository import InMemoryTaskRepository
from ex11_service import TaskService
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Iterator[TestClient]:
    """app.dependency_overrides ≈ replacing the @Bean for the test's scope."""
    fresh = TaskService(InMemoryTaskRepository())
    app.dependency_overrides[get_task_service] = lambda: fresh
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_with_priority(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "important", "priority": "high"})
    assert response.status_code == 201, f"got {response.status_code}: {response.text}"
    assert response.json()["priority"] == "high"


def test_create_defaults_to_medium(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "ordinary"})
    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_invalid_priority_gets_422(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "x", "priority": "urgent"})
    assert response.status_code == 422


def test_filter_by_priority(client: TestClient) -> None:
    client.post("/tasks", json={"title": "a", "priority": "high"})
    client.post("/tasks", json={"title": "b"})  # medium
    client.post("/tasks", json={"title": "c", "priority": "high"})
    response = client.get("/tasks/by-priority/high")
    assert response.status_code == 200, "implement the service method + the router endpoint"
    assert [t["title"] for t in response.json()] == ["a", "c"]


def test_update_priority(client: TestClient) -> None:
    created = client.post("/tasks", json={"title": "escalate me"})
    task_id = created.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"priority": "high"})
    assert response.status_code == 200
    assert response.json()["priority"] == "high"
