"""The full auth flow, end to end (≈ Spring Security integration tests).

register -> login -> access protected endpoint
         -> 401 without token -> 401 with tampered token -> 401 with expired token
"""

from fastapi.testclient import TestClient

GOOD_PASSWORD = "supersecret1"


def test_register_returns_201_without_password(client: TestClient, username: str) -> None:
    response = client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == username
    assert "password" not in body  # the hash never leaves the server


def test_register_duplicate_username_returns_409(client: TestClient, username: str) -> None:
    payload = {"username": username, "password": GOOD_PASSWORD}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_register_short_password_returns_422(client: TestClient, username: str) -> None:
    response = client.post("/auth/register", json={"username": username, "password": "short"})
    assert response.status_code == 422


def test_login_returns_bearer_token(client: TestClient, username: str) -> None:
    client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    response = client.post("/auth/token", data={"username": username, "password": GOOD_PASSWORD})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2  # JWT shape: header.payload.signature


def test_login_wrong_password_returns_401(client: TestClient, username: str) -> None:
    client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    response = client.post("/auth/token", data={"username": username, "password": "wrong-password"})
    assert response.status_code == 401


def test_login_unknown_user_returns_401(client: TestClient) -> None:
    response = client.post("/auth/token", data={"username": "ghost", "password": "whatever123"})
    assert response.status_code == 401


def test_protected_endpoint_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_with_token_returns_200(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/tasks", headers=auth_headers).status_code == 200


def test_tampered_token_returns_401(client: TestClient, auth_headers: dict[str, str]) -> None:
    # Flip the signature: a modified token must not validate (integrity check).
    token = auth_headers["Authorization"].removeprefix("Bearer ")
    tampered = token[:-2] + ("AA" if not token.endswith("AA") else "BB")
    response = client.get("/tasks", headers={"Authorization": f"Bearer {tampered}"})
    assert response.status_code == 401


def test_expired_token_returns_401(client: TestClient, username: str) -> None:
    from secureapp.dependencies import get_settings
    from secureapp.security import create_access_token

    client.post("/auth/register", json={"username": username, "password": GOOD_PASSWORD})
    settings = get_settings()
    expired = create_access_token(
        subject=username,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expires_minutes=-1,  # already expired
    )
    response = client.get("/tasks", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_token_signed_with_wrong_key_returns_401(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    from secureapp.dependencies import get_settings
    from secureapp.security import create_access_token

    forged = create_access_token(
        subject="admin",
        secret_key="not-the-server-key-but-32-bytes-long",
        algorithm=get_settings().algorithm,
        expires_minutes=5,
    )
    assert client.get("/tasks", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
