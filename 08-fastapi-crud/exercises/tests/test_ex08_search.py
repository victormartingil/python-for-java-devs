"""Spec for ex03 (GET /tasks?q=...) — make these pass."""

from ex08_app import app
from fastapi.testclient import TestClient


def test_search_matches_case_insensitively() -> None:
    client = TestClient(app)
    client.post("/tasks", json={"title": "search-probe FIX login"})
    client.post("/tasks", json={"title": "search-probe fix docs"})
    client.post("/tasks", json={"title": "search-probe ship release"})
    response = client.get("/tasks", params={"q": "fix"})
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert "search-probe FIX login" in titles
    assert "search-probe fix docs" in titles
    assert "search-probe ship release" not in titles


def test_search_without_match_returns_empty() -> None:
    client = TestClient(app)
    client.post("/tasks", json={"title": "search-probe ordinary task"})
    response = client.get("/tasks", params={"q": "zzz-no-such-fragment"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_without_q_still_works() -> None:
    client = TestClient(app)
    assert client.get("/tasks").status_code == 200
