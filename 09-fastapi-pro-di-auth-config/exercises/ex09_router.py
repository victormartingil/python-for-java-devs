"""Exercise 09-01 — protect a new endpoint with CurrentUserDep.

A /me endpoint: return the authenticated user. The dependency does ALL the
security work — your job is one line. The tests are the spec:

    uv run pytest 09-fastapi-pro-di-auth-config/exercises -v

Hint: every endpoint in 09-fastapi-pro-di-auth-config/secureapp/tasks_router.py
declares `current_user: CurrentUserDep`. The dependency itself
(secureapp/dependencies.py) is ≈ the Spring Security filter + principal
resolution: no valid token -> 401 before your code runs.
"""

from fastapi import APIRouter
from secureapp.dependencies import CurrentUserDep
from secureapp.schemas import UserResponse

router = APIRouter(tags=["exercises"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUserDep) -> UserResponse:
    """TODO(ex01): return the current user.

    Yes — one line. The dependency already rejected unauthenticated requests
    with a 401 before this body runs. That IS the exercise: noticing how much
    a Depends() alias gives you for free.
    """
    raise NotImplementedError("TODO(ex01): return current_user")
