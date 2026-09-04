from sqlalchemy.orm import Session

from models.favorite_restaurant import FavoriteRestaurant


class FavoriteRestaurantRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        user_id: int,
        restaurant_id: int,
    ):
        favorite = FavoriteRestaurant(
            user_id=user_id,
            restaurant_id=restaurant_id,
        )

        self.db.add(favorite)
        self.db.flush()

        return favorite

    def get_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(FavoriteRestaurant)
            .filter(
                FavoriteRestaurant.user_id == user_id
            )
            .all()
        )

    def get_by_user_and_restaurant(
        self,
        user_id: int,
        restaurant_id: int,
    ):
        return (
            self.db.query(FavoriteRestaurant)
            .filter(
                FavoriteRestaurant.user_id == user_id,
                FavoriteRestaurant.restaurant_id == restaurant_id,
            )
            .first()
        )

    def delete(
        self,
        favorite: FavoriteRestaurant,
    ):
        self.db.delete(favorite)
        self.db.flush()