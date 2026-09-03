from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dto.user import UserResponse, UserUpdate, AdminUserUpdate
from services.user_service import UserService
from dependencies.auth import get_current_user, get_current_admin
from models.user import User
from config.database import get_db
from typing import List
from dto.address import AddressCreate, AddressResponse
from services.address_service import AddressService
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



@router.post(
    "/me/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address_data: AddressCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    address_service = AddressService(db)

    try:
        address = address_service.create_address(
            address_data=address_data,
            user_id=current_user.id,
        )

        db.commit()

        return address

    except Exception:
        db.rollback()
        raise


@router.get(
    "/me/addresses",
    response_model=list[AddressResponse],
)
def get_my_addresses(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    address_service = AddressService(db)

    return address_service.get_user_addresses(
        user_id=current_user.id,
    )