from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_admin_or_restaurant_owner
from dto.menu_item import MenuItemCreate, MenuItemResponse
from models.user import User
from services.menu_item_service import MenuItemService


router = APIRouter(
    prefix="/menus",
    tags=["Menu Items"],
)


@router.put(
    "/{menu_id}/items/{food_id}",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_food_to_menu(
    menu_id: int,
    food_id: int,
    menu_item_data: MenuItemCreate,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    menu_item_service = MenuItemService(db)

    try:
        menu_item = menu_item_service.add_food_to_menu(
            menu_id=menu_id,
            food_id=food_id,
            menu_item_data=menu_item_data,
            current_user=current_user,
        )

        db.commit()
        return menu_item

    except Exception:
        db.rollback()
        raise


@router.delete(
    "/{menu_id}/items/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_food_from_menu(
    menu_id: int,
    food_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    menu_item_service = MenuItemService(db)

    try:
        menu_item_service.remove_food_from_menu(
            menu_id=menu_id,
            food_id=food_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return None


@router.get(
    "/{menu_id}/items",
    response_model=list[MenuItemResponse],
)
def get_menu_items(
    menu_id: int,
    db: Session = Depends(get_db),
):
    menu_item_service = MenuItemService(db)

    return menu_item_service.get_menu_items(
        menu_id=menu_id,
    )