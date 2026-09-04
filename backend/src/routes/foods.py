from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import (
    get_current_admin_or_restaurant_owner,
)
from dto.food import (
    FoodResponse,
    FoodUpdate,
)
from dto.food_category import (
    FoodCategoryAssign,
    FoodCategoryResponse,
)
from models.user import User
from services.food_category_service import FoodCategoryService
from services.food_service import FoodService


router = APIRouter(
    prefix="/foods",
    tags=["Foods"],
)


# Get a single food item by its id. Public endpoint.
@router.get(
    "/{food_id}",
    response_model=FoodResponse,
)
def get_food(
    food_id: int,
    db: Session = Depends(get_db),
):
    food_service = FoodService(db)

    return food_service.get_food_by_id(
        food_id=food_id,
    )


# Partially update a food item. Accessible to an admin or the owning
# restaurant's owner.
@router.patch(
    "/{food_id}",
    response_model=FoodResponse,
)
def update_food(
    food_id: int,
    food_data: FoodUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    food_service = FoodService(db)

    try:
        food = food_service.update_food(
            food_id=food_id,
            food_data=food_data,
            current_user=current_user,
        )

        db.commit()

        return food

    except Exception:
        db.rollback()
        raise


# Delete a food item by id. Accessible to an admin or the owning restaurant's
# owner. Returns 204 with no content.
@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_food(
    food_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    food_service = FoodService(db)

    try:
        food_service.delete_food(
            food_id=food_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


# List all categories assigned to a food item. Public endpoint.
@router.get(
    "/{food_id}/categories",
    response_model=list[FoodCategoryResponse],
)
def get_food_categories(
    food_id: int,
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    return category_service.get_food_categories(
        food_id=food_id,
    )


# Assign one or more categories to a food item. Accessible to an admin
# or the owning restaurant's owner.
@router.post(
    "/{food_id}/categories",
    response_model=list[FoodCategoryResponse],
    status_code=status.HTTP_200_OK,
)
def add_categories_to_food(
    food_id: int,
    category_data: FoodCategoryAssign,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    try:
        categories = category_service.add_categories_to_food(
            food_id=food_id,
            category_ids=category_data.category_ids,
            current_user=current_user,
        )

        db.commit()

        return categories

    except Exception:
        db.rollback()
        raise


# Remove a single category from a food item. Accessible to an admin
# or the owning restaurant's owner. Returns 204 with no content.
@router.delete(
    "/{food_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_category_from_food(
    food_id: int,
    category_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    try:
        category_service.remove_category_from_food(
            food_id=food_id,
            category_id=category_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise