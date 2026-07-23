"""API integration tests: real app + TestClient, repositories overridden.

No database involved — the in-memory adapters are injected in conftest.py
via app.dependency_overrides. Compare with module 10's tests, which hit real
PostgreSQL: same HTTP contract, different adapter. That's the architecture
paying rent.
"""

from fastapi.testclient import TestClient

GOOD_PASSWORD = "supersecret1"


def test_full_auth_and_crud_flow(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post("/tasks", json={"title": "layered task"}, headers=auth_headers)
    assert created.status_code == 201
    task_id = created.json()["id"]

    fetched = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json() == {
        "id": task_id,
        "title": "layered task",
        "description": None,
        "completed": False,
    }

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True}, headers=auth_headers)
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    assert client.delete(f"/tasks/{task_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 404


def test_register_login_roundtrip(client: TestClient) -> None:
    assert (
        client.post(
            "/auth/register", json={"username": "carol", "password": GOOD_PASSWORD}
        ).status_code
        == 201
    )
    response = client.post("/auth/token", data={"username": "carol", "password": GOOD_PASSWORD})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_duplicate_registration_returns_409(client: TestClient) -> None:
    payload = {"username": "dave", "password": GOOD_PASSWORD}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_wrong_password_returns_401(client: TestClient) -> None:
    client.post("/auth/register", json={"username": "erin", "password": GOOD_PASSWORD})
    response = client.post("/auth/token", data={"username": "erin", "password": "wrong-password"})
    assert response.status_code == 401


def test_tasks_require_authentication(client: TestClient) -> None:
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "x"}).status_code == 401


def test_domain_not_found_maps_to_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    # The service raises NotFoundError; core/exceptions.py maps it — the router
    # contains no error handling at all.
    assert client.get("/tasks/999", headers=auth_headers).status_code == 404


def test_validation_error_maps_to_422(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert client.post("/tasks", json={"title": ""}, headers=auth_headers).status_code == 422
