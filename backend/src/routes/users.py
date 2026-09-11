from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import (
    get_current_admin,
    get_current_restaurant_owner,
    get_current_user,
)
from dto.address import AddressCreate, AddressResponse
from dto.restaurant import RestaurantResponse
from dto.user import AdminUserUpdate, UserResponse, UserUpdate
from models.user import User
from services.address_service import AddressService
from services.restaurant_service import RestaurantService
from services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# Get the currently authenticated user's own profile.
@router.get(
    "/me",
    response_model=UserResponse,
)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


# Update the currently authenticated user's own profile. Raises 409 on a
# conflicting value (e.g. duplicate phone/email).
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


# List all users. Admin-only endpoint.
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


# Get a single user by id. Admin-only endpoint. Raises 404 if not found.
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


# Update any user's account as an admin (e.g. role, status). Admin-only
# endpoint. Raises 404 if the user doesn't exist, 409 on a conflicting value.
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
            current_admin=current_admin,
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


# Add a new address for the currently authenticated user.
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


# List all addresses belonging to the currently authenticated user.
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


# List all restaurants owned by the currently authenticated user.
# Requires the RESTAURANT_OWNER role.
@router.get(
    "/me/restaurants",
    response_model=list[RestaurantResponse],
)
def get_my_restaurants(
    current_user: Annotated[User, Depends(get_current_restaurant_owner)],
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)

    return restaurant_service.get_my_restaurants(
        user_id=current_user.id
    )