from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from repositories.favorite_restaurant_repository import (
    FavoriteRestaurantRepository,
)
from repositories.restaurant_repository import RestaurantRepository


class FavoriteRestaurantService:
    def __init__(self, db: Session):
        self.favorite_repository = FavoriteRestaurantRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def add_favorite(
        self,
        user: User,
        restaurant_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        existing_favorite = (
            self.favorite_repository.get_by_user_and_restaurant(
                user_id=user.id,
                restaurant_id=restaurant_id,
            )
        )

        if existing_favorite is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Restaurant is already in favorites",
            )

        return self.favorite_repository.add(
            user_id=user.id,
            restaurant_id=restaurant_id,
        )

    def get_user_favorites(
        self,
        user: User,
    ):
        return self.favorite_repository.get_by_user_id(
            user_id=user.id
        )

    def remove_favorite(
        self,
        user: User,
        restaurant_id: int,
    ):
        favorite = (
            self.favorite_repository.get_by_user_and_restaurant(
                user_id=user.id,
                restaurant_id=restaurant_id,
            )
        )

        if favorite is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant is not in favorites",
            )

        self.favorite_repository.delete(favorite)

        return favorite