"""Auth endpoints ≈ a @RestController for registration and login.

POST /auth/register  -> 201 + UserResponse (409 if username taken)
POST /auth/token     -> OAuth2 password flow: form-encoded username/password,
                        returns a JWT. This is the standard shape Swagger UI,
                        curl and every OAuth2 client already understand.

Run the API:  uv run uvicorn secureapp.main:app --reload   (from 09-fastapi-pro-di-auth-config/)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from secureapp.dependencies import SettingsDep, UserStoreDep
from secureapp.schemas import Token, UserCreate, UserResponse
from secureapp.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, users: UserStoreDep) -> UserResponse:
    # Never store the plain password — hash with Argon2id at the boundary.
    user = users.create(data.username, hash_password(data.password))
    return UserResponse(id=user.id, username=user.username)


@router.post("/token", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: UserStoreDep,
    settings: SettingsDep,
) -> Token:
    # OAuth2PasswordRequestForm parses application/x-www-form-urlencoded
    # username/password — the OAuth2 password-grant contract.
    user = users.get_by_username(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        # Same message for "no such user" and "wrong password" — don't leak which.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(
            subject=user.username,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            expires_minutes=settings.access_token_expire_minutes,
        )
    )
