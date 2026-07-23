"""Spec for ex01 (GET /me) — make these pass."""

from fastapi.testclient import TestClient


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/me").status_code == 401


def test_me_returns_the_authenticated_user(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] >= 1
    assert body["username"].startswith("user_")
