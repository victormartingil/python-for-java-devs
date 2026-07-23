"""DI with Depends ≈ @Autowired / constructor injection.

A dependency is just a function. FastAPI calls it per request and injects the
result. Dependencies can depend on other dependencies — FastAPI builds the
graph (≈ the Spring container wiring beans):

    endpoint
      └─ get_current_user
           ├─ oauth2_scheme      (extracts the Bearer token from the header)
           ├─ get_settings       (lru_cached singleton ≈ @ConfigurationProperties bean)
           └─ get_user_store     (the in-memory "repository" — swap for SQL in module 10)

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from secureapp.config import Settings
from secureapp.schemas import UserResponse
from secureapp.security import decode_access_token
from secureapp.stores import TaskStore, UserStore, task_store, user_store

# OAuth2PasswordBearer does two jobs: (1) extracts "Authorization: Bearer <token>",
# returning 401 automatically if absent; (2) tells Swagger UI to show the
# login flow — you can authenticate inside /docs with the "Authorize" button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@lru_cache  # one Settings instance for the process ≈ a singleton bean
def get_settings() -> Settings:
    return Settings()


def get_user_store() -> UserStore:
    return user_store


def get_task_store() -> TaskStore:
    return task_store


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
    users: Annotated[UserStore, Depends(get_user_store)],
) -> UserResponse:
    """≈ a Spring Security filter + AuthenticationPrincipal resolution.

    Any endpoint that declares `current_user: CurrentUser = Depends(get_current_user)`
    is protected: no valid token -> 401 before the endpoint body runs.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(
            token, secret_key=settings.secret_key, algorithm=settings.algorithm
        )
    except InvalidTokenError:  # expired, tampered, malformed — all land here
        raise credentials_error from None
    username = payload.get("sub")
    user = users.get_by_username(username) if isinstance(username, str) else None
    if user is None:
        raise credentials_error
    return UserResponse(id=user.id, username=user.username)


# Reusable annotated aliases — the modern FastAPI style for endpoint signatures.
SettingsDep = Annotated[Settings, Depends(get_settings)]
TaskStoreDep = Annotated[TaskStore, Depends(get_task_store)]
UserStoreDep = Annotated[UserStore, Depends(get_user_store)]
CurrentUserDep = Annotated[UserResponse, Depends(get_current_user)]
