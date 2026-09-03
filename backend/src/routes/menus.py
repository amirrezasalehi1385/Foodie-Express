from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import (
    get_current_admin_or_restaurant_owner,
)
from dto.menu import MenuResponse, MenuUpdate
from models.user import User
from services.menu_service import MenuService

router = APIRouter(
    prefix="/menus",
    tags=["Menus"],
)


# Get a single menu by its id. Public endpoint.
@router.get(
    "/{menu_id}",
    response_model=MenuResponse,
)
def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
):
    menu_service = MenuService(db)

    return menu_service.get_menu_by_id(
        menu_id=menu_id,
    )


# Partially update a menu. Accessible to an admin or the owning restaurant's owner.
@router.patch(
    "/{menu_id}",
    response_model=MenuResponse,
)
def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    menu_service = MenuService(db)

    try:
        menu = menu_service.update_menu(
            menu_id=menu_id,
            menu_data=menu_data,
            current_user=current_user,
        )

        db.commit()

        return menu

    except Exception:
        db.rollback()
        raise


# Delete a menu by id. Accessible to an admin or the owning restaurant's owner.
# Returns 204 with no content on success.
@router.delete(
    "/{menu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_menu(
    menu_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    menu_service = MenuService(db)

    try:
        menu_service.delete_menu(
            menu_id=menu_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise