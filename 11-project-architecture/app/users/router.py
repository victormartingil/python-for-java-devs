"""Auth HTTP layer ≈ @RestController for registration and login. Thin.

Run:  docker compose up -d && uv run alembic upgrade head
      uv run uvicorn app.main:app --reload   (from 11-project-architecture/)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import UserServiceDep
from app.users.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, service: UserServiceDep) -> UserResponse:
    return await service.register(data)  # UsernameTakenError -> 409 via core/exceptions.py


@router.post("/token", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserServiceDep
) -> Token:
    return await service.login(form.username, form.password)
