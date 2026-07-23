"""Integration tests with TestClient ≈ @SpringBootTest + MockMvc.

TestClient runs the ASGI app in-process over HTTP semantics (built on httpx):
same requests, same status codes, same JSON — no server to start.
"""

import pytest
from fastapi.testclient import TestClient
from tasks_app import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def task_id(client: TestClient) -> int:
    """A task that exists for the duration of one test."""
    response = client.post("/tasks", json={"title": "write module 08"})
    assert response.status_code == 201
    return response.json()["id"]


# --- Create --------------------------------------------------------------------
def test_create_task_returns_201_and_body(client: TestClient) -> None:
    response = client.post(
        "/tasks", json={"title": "learn FastAPI", "description": "build the CRUD"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["title"] == "learn FastAPI"
    assert body["completed"] is False  # schema default applied


# --- Read ----------------------------------------------------------------------
def test_get_task(client: TestClient, task_id: int) -> None:
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "write module 08"


def test_get_missing_task_returns_404(client: TestClient) -> None:
    assert client.get("/tasks/999999").status_code == 404


def test_list_tasks_contains_created_task(client: TestClient, task_id: int) -> None:
    ids = [t["id"] for t in client.get("/tasks").json()]
    assert task_id in ids


def test_list_tasks_filter_by_completed(client: TestClient, task_id: int) -> None:
    client.patch(f"/tasks/{task_id}", json={"completed": True})
    completed_ids = [t["id"] for t in client.get("/tasks", params={"completed": True}).json()]
    pending_ids = [t["id"] for t in client.get("/tasks", params={"completed": False}).json()]
    assert task_id in completed_ids
    assert task_id not in pending_ids


# --- Update --------------------------------------------------------------------
def test_patch_updates_only_sent_fields(client: TestClient, task_id: int) -> None:
    response = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    body = response.json()
    assert body["completed"] is True
    assert body["title"] == "write module 08"  # untouched field preserved


def test_patch_missing_task_returns_404(client: TestClient) -> None:
    assert client.patch("/tasks/999999", json={"completed": True}).status_code == 404


# --- Delete --------------------------------------------------------------------
def test_delete_task_returns_204_then_404(client: TestClient, task_id: int) -> None:
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_missing_task_returns_404(client: TestClient) -> None:
    assert client.delete("/tasks/999999").status_code == 404


# --- Validation: automatic 422 ≈ MethodArgumentNotValidException -----------------
def test_missing_title_returns_422(client: TestClient) -> None:
    assert client.post("/tasks", json={}).status_code == 422


def test_empty_title_returns_422(client: TestClient) -> None:
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_unknown_field_returns_422(client: TestClient) -> None:
    # extra="forbid": silent field swallowing is a classic source of bugs
    response = client.post("/tasks", json={"title": "x", "admin": True})
    assert response.status_code == 422


def test_wrong_path_param_type_returns_422(client: TestClient) -> None:
    assert client.get("/tasks/not-an-int").status_code == 422
