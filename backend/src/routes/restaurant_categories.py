from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from dto.restaurant_category import (
    RestaurantCategoryCreate,
    RestaurantCategoryResponse,
    RestaurantCategoryUpdate,
)
from models.user import User
from services.restaurant_category_service import RestaurantCategoryService


router = APIRouter(
    prefix="/restaurant-categories",
    tags=["Restaurant Categories"],
)


@router.post(
    "",
    response_model=RestaurantCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: RestaurantCategoryCreate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

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


@router.get(
    "",
    response_model=list[RestaurantCategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

    return category_service.get_all_categories()


@router.get(
    "/{category_id}",
    response_model=RestaurantCategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

    return category_service.get_category_by_id(
        category_id=category_id,
    )


@router.patch(
    "/{category_id}",
    response_model=RestaurantCategoryResponse,
)
def update_category(
    category_id: int,
    category_data: RestaurantCategoryUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

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
    category_service = RestaurantCategoryService(db)

    try:
        category_service.delete_category(
            category_id=category_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return None