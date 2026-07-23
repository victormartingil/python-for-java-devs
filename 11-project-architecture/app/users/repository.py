"""User data access — same structural-Protocol pattern as tasks/repository.py.

UserRecord carries the password hash (the service needs it to verify logins),
but it never reaches the HTTP layer — schemas.UserResponse is the public shape.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import UserModel


@dataclass
class UserRecord:
    id: int
    username: str
    hashed_password: str


class UserRepository(Protocol):
    """Structural contract (≈ the repository port) — no `implements` needed."""

    async def get_by_username(self, username: str) -> UserRecord | None: ...
    async def create(self, username: str, hashed_password: str) -> UserRecord: ...


def _to_record(user: UserModel) -> UserRecord:
    return UserRecord(id=user.id, username=user.username, hashed_password=user.hashed_password)


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_username(self, username: str) -> UserRecord | None:
        statement = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(statement)
        user = result.scalar_one_or_none()
        return _to_record(user) if user is not None else None

    async def create(self, username: str, hashed_password: str) -> UserRecord:
        user = UserModel(username=username, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return _to_record(user)


class InMemoryUserRepository:
    """Test adapter — swapped in via app.dependency_overrides (see tests/)."""

    def __init__(self) -> None:
        self._rows: dict[str, UserRecord] = {}
        self._next_id: int = 1

    async def get_by_username(self, username: str) -> UserRecord | None:
        return self._rows.get(username)

    async def create(self, username: str, hashed_password: str) -> UserRecord:
        record = UserRecord(id=self._next_id, username=username, hashed_password=hashed_password)
        self._rows[username] = record
        self._next_id += 1
        return record
