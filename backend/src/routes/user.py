from typing import Annotated

from fastapi import APIRouter, Depends

from dto.user import UserResponse
from dependencies.auth import get_current_user
from models.user import User


router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user