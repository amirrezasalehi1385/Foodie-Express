from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dto.user import UserResponse, UserUpdate, AdminUserUpdate
from services.user_service import UserService
from dependencies.auth import get_current_user, get_current_admin
from models.user import User
from config.database import get_db
from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

@router.patch(
    "/me",
    response_model=UserResponse,
)


def update_my_profile(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    try:
        user = user_service.update_user(
            user=current_user,
            user_data=user_data,
        )

        db.commit()

        return user

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    return user_service.get_users()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def admin_update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        user = user_service.admin_update_user(
            user=user,
            user_data=user_data,
        )

        db.commit()

        return user

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )
    