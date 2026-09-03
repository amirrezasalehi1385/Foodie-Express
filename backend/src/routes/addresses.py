from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from dto.address import AddressResponse, AddressUpdate
from models.user import User
from services.address_service import AddressService

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)


# Get a single address by id, scoped to the current authenticated user.
@router.get(
    "/{address_id}",
    response_model=AddressResponse,
)
def get_address(
    address_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    address_service = AddressService(db)

    return address_service.get_address_by_id(
        address_id=address_id,
        user_id=current_user.id,
    )


# Partially update an address belonging to the current authenticated user.
@router.patch(
    "/{address_id}",
    response_model=AddressResponse,
)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    address_service = AddressService(db)

    try:
        address = address_service.update_address(
            address_id=address_id,
            address_data=address_data,
            user_id=current_user.id,
        )

        db.commit()

        return address

    except Exception:
        db.rollback()
        raise


# Delete an address belonging to the current authenticated user. Returns 204
# with no content on success.
@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_address(
    address_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    address_service = AddressService(db)

    try:
        address_service.delete_address(
            address_id=address_id,
            user_id=current_user.id,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise