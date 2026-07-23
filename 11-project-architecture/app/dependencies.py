"""DI wiring with Depends ≈ @Configuration + @Bean — the composition root for objects.

Every swappable object is constructed HERE, in one visible place:

    endpoint
      └─ TaskServiceDep        → get_task_service
           └─ TaskRepositoryDep → get_task_repository
                └─ get_session  → per-request AsyncSession (≈ OpenSessionInView + tx)

Swap Postgres for in-memory and NO domain code changes — tests do exactly
that with app.dependency_overrides (≈ @MockBean; see tests/conftest.py).
That is the ports & adapters payoff, delivered by duck typing + DI.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import async_session_factory
from app.core.security import decode_access_token
from app.tasks.repository import SqlAlchemyTaskRepository, TaskRepository
from app.tasks.service import TaskService
from app.users.repository import SqlAlchemyUserRepository, UserRepository
from app.users.schemas import UserResponse
from app.users.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_session() -> AsyncIterator[AsyncSession]:
    """Session per request; commit on success, rollback on exception."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- tasks module wiring -------------------------------------------------------
def get_task_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TaskRepository:
    # Annotated as the PROTOCOL: tests override this to return InMemoryTaskRepository.
    return SqlAlchemyTaskRepository(session)


def get_task_service(repo: Annotated[TaskRepository, Depends(get_task_repository)]) -> TaskService:
    return TaskService(repo)


# --- users module wiring -------------------------------------------------------
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_user_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserService:
    return UserService(
        users,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        token_expire_minutes=settings.access_token_expire_minutes,
    )


# --- security -------------------------------------------------------------------
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserResponse:
    """Any endpoint depending on this is protected (≈ Spring Security filter chain)."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(
            token, secret_key=settings.secret_key, algorithm=settings.algorithm
        )
    except InvalidTokenError:
        raise credentials_error from None
    username = payload.get("sub")
    user = await users.get_by_username(username) if isinstance(username, str) else None
    if user is None:
        raise credentials_error
    return UserResponse(id=user.id, username=user.username)


# Reusable annotated aliases — endpoints stay one line long.
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
CurrentUserDep = Annotated[UserResponse, Depends(get_current_user)]
