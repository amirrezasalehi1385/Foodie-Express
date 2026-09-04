from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from dto.favorite_restaurant import FavoriteRestaurantResponse
from models.user import User
from services.favorite_restaurant_service import (
    FavoriteRestaurantService,
)

router = APIRouter(
    prefix="/users/me/favorites",
    tags=["Favorites"],
)


@router.get(
    "",
    response_model=list[FavoriteRestaurantResponse],
)
def get_user_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    favorite_service = FavoriteRestaurantService(db)

    return favorite_service.get_user_favorites(
        user=current_user,
    )


@router.post(
    "/{restaurant_id}",
    response_model=FavoriteRestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    restaurant_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    favorite_service = FavoriteRestaurantService(db)

    try:
        favorite = favorite_service.add_favorite(
            user=current_user,
            restaurant_id=restaurant_id,
        )

        db.commit()

        return favorite

    except Exception:
        db.rollback()
        raise

@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_favorite(
    restaurant_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    favorite_service = FavoriteRestaurantService(db)

    try:
        favorite_service.remove_favorite(
            user=current_user,
            restaurant_id=restaurant_id,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise