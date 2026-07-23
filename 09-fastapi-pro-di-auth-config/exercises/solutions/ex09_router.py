"""SOLUTION 09-01 — don't peek until your tests pass.

Reference implementation; yours may differ and still be correct.
"""

from fastapi import APIRouter
from secureapp.dependencies import CurrentUserDep
from secureapp.schemas import UserResponse

router = APIRouter(tags=["exercises"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUserDep) -> UserResponse:
    return current_user
