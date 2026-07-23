"""Pure user-service tests: registration rules and login, no framework."""

import pytest
from app.core.exceptions import InvalidCredentialsError, UsernameTakenError
from app.core.security import decode_access_token
from app.users.repository import InMemoryUserRepository
from app.users.schemas import UserCreate
from app.users.service import UserService

TEST_SECRET = "test-secret-key-do-not-use-in-prod"
TEST_ALGORITHM = "HS256"


@pytest.fixture
def service() -> UserService:
    return UserService(
        InMemoryUserRepository(),
        secret_key=TEST_SECRET,
        algorithm=TEST_ALGORITHM,
        token_expire_minutes=30,
    )


async def test_register_returns_public_shape(service: UserService) -> None:
    user = await service.register(UserCreate(username="bob", password="supersecret1"))
    assert user.username == "bob"
    assert "hashed_password" not in user.model_dump()  # the hash stays server-side


async def test_register_duplicate_username_rejected(service: UserService) -> None:
    await service.register(UserCreate(username="bob", password="supersecret1"))
    with pytest.raises(UsernameTakenError):
        await service.register(UserCreate(username="bob", password="anotherpass1"))


async def test_login_issues_verifiable_token(service: UserService) -> None:
    await service.register(UserCreate(username="bob", password="supersecret1"))
    token = await service.login("bob", "supersecret1")
    assert token.token_type == "bearer"
    payload = decode_access_token(
        token.access_token, secret_key=TEST_SECRET, algorithm=TEST_ALGORITHM
    )
    assert payload["sub"] == "bob"


async def test_login_wrong_password_rejected(service: UserService) -> None:
    await service.register(UserCreate(username="bob", password="supersecret1"))
    with pytest.raises(InvalidCredentialsError):
        await service.login("bob", "wrong-password")


async def test_login_unknown_user_rejected(service: UserService) -> None:
    with pytest.raises(InvalidCredentialsError):
        await service.login("ghost", "whatever123")
