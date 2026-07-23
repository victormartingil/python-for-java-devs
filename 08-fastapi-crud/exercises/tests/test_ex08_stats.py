"""Spec for ex01 (GET /tasks/stats) — make these pass."""

from ex08_app import app
from fastapi.testclient import TestClient


def test_stats_shape() -> None:
    client = TestClient(app)
    response = client.get("/tasks/stats")
    assert response.status_code == 200
    assert set(response.json()) == {"total", "completed", "pending"}


def test_stats_counts_track_created_tasks() -> None:
    client = TestClient(app)
    before = client.get("/tasks/stats").json()
    client.post("/tasks", json={"title": "stats probe one"})
    client.post("/tasks", json={"title": "stats probe two", "completed": True})
    after = client.get("/tasks/stats").json()
    assert after["total"] == before["total"] + 2
    assert after["completed"] == before["completed"] + 1
    assert after["pending"] == before["pending"] + 1


def test_stats_is_not_swallowed_by_the_task_id_route() -> None:
    # /tasks/stats must NOT match GET /tasks/{task_id} — route order matters.
    client = TestClient(app)
    response = client.get("/tasks/stats")
    assert response.status_code != 422, (
        "'stats' was parsed as a task id — declare /stats before /{task_id}"
    )
