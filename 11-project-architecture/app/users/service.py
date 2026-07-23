"""User business logic: register, login. No FastAPI, no SQLAlchemy.

Even configuration arrives as plain constructor values (secret_key, algorithm,
token_expire_minutes) — dependencies.py extracts them from Settings. The
service is testable with nothing but pytest (see tests/test_user_service.py).

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from app.core.exceptions import InvalidCredentialsError, UsernameTakenError
from app.core.security import create_access_token, hash_password, verify_password
from app.users.repository import UserRepository
from app.users.schemas import Token, UserCreate, UserResponse


class UserService:
    def __init__(
        self,
        users: UserRepository,
        *,
        secret_key: str,
        algorithm: str,
        token_expire_minutes: int,
    ) -> None:
        self._users = users
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_expire_minutes = token_expire_minutes

    async def register(self, data: UserCreate) -> UserResponse:
        if await self._users.get_by_username(data.username) is not None:
            raise UsernameTakenError(f"username '{data.username}' is already taken")
        record = await self._users.create(data.username, hash_password(data.password))
        return UserResponse.model_validate(record)

    async def login(self, username: str, password: str) -> Token:
        record = await self._users.get_by_username(username)
        # Same error for unknown user and wrong password — don't leak which.
        if record is None or not verify_password(password, record.hashed_password):
            raise InvalidCredentialsError()
        return Token(
            access_token=create_access_token(
                subject=record.username,
                secret_key=self._secret_key,
                algorithm=self._algorithm,
                expires_minutes=self._token_expire_minutes,
            )
        )
