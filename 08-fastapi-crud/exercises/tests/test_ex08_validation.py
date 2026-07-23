"""Spec for ex02 (title validation in TaskCreate) — make these pass."""

from ex08_app import app
from fastapi.testclient import TestClient


def test_whitespace_only_title_is_rejected() -> None:
    client = TestClient(app)
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422, (
        "whitespace-only titles must be rejected — add a field_validator in ex08_schemas.py"
    )


def test_title_is_stripped_on_create() -> None:
    client = TestClient(app)
    response = client.post("/tasks", json={"title": "  padded  "})
    assert response.status_code == 201
    assert response.json()["title"] == "padded"


def test_normal_titles_still_work() -> None:
    client = TestClient(app)
    assert client.post("/tasks", json={"title": "clean"}).status_code == 201
