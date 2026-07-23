"""Secured CRUD: same behavior as module 08, now behind a JWT.

Also verifies the global exception handlers (≈ @ControllerAdvice): no
try/except in the endpoints, still proper 404s.
"""

from fastapi.testclient import TestClient


def test_full_crud_flow_with_auth(client: TestClient, auth_headers: dict[str, str]) -> None:
    # create
    created = client.post("/tasks", json={"title": "secure task"}, headers=auth_headers)
    assert created.status_code == 201
    task_id = created.json()["id"]

    # read
    fetched = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "secure task"

    # update
    updated = client.patch(f"/tasks/{task_id}", json={"completed": True}, headers=auth_headers)
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    # delete
    assert client.delete(f"/tasks/{task_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404


def test_every_tasks_endpoint_requires_auth(client: TestClient) -> None:
    assert client.post("/tasks", json={"title": "x"}).status_code == 401
    assert client.get("/tasks").status_code == 401
    assert client.get("/tasks/1").status_code == 401
    assert client.patch("/tasks/1", json={"completed": True}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401


def test_missing_task_returns_404_via_global_handler(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/tasks/999999", headers=auth_headers).status_code == 404


def test_middleware_adds_process_time_header(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/tasks", headers=auth_headers)
    assert "x-process-time-ms" in response.headers


def test_health_endpoint_is_public(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
