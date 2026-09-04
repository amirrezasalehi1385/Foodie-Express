from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from dto.food_category import (
    FoodCategoryCreate,
    FoodCategoryResponse,
    FoodCategoryUpdate,
)
from models.user import User
from services.food_category_service import FoodCategoryService


router = APIRouter(
    prefix="/food-categories",
    tags=["Food Categories"],
)


# Create a new food category. Requires admin access.
@router.post(
    "",
    response_model=FoodCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: FoodCategoryCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    try:
        category = category_service.create_category(
            category_data=category_data,
            current_user=current_user,
        )

        db.commit()

        return category

    except Exception:
        db.rollback()
        raise


# List all food categories. Public endpoint.
@router.get(
    "",
    response_model=list[FoodCategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    return category_service.get_all_categories()


# Get a single food category by id. Public endpoint.
@router.get(
    "/{category_id}",
    response_model=FoodCategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    return category_service.get_category_by_id(
        category_id=category_id,
    )


# Partially update a food category. Requires admin access.
@router.patch(
    "/{category_id}",
    response_model=FoodCategoryResponse,
)
def update_category(
    category_id: int,
    category_data: FoodCategoryUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    try:
        category = category_service.update_category(
            category_id=category_id,
            category_data=category_data,
            current_user=current_user,
        )

        db.commit()

        return category

    except Exception:
        db.rollback()
        raise


# Delete a food category by id. Requires admin access.
# Returns 204 with no content on success.
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    category_service = FoodCategoryService(db)

    try:
        category_service.delete_category(
            category_id=category_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise