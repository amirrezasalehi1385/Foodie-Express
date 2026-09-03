from sqlalchemy.orm import Session

from models.food import Food
from repositories.base_repository import BaseRepository


class FoodRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Food)

    def get_by_restaurant_id(
        self,
        restaurant_id: int,
    ):
        return (
            self.db.query(Food)
            .filter(Food.restaurant_id == restaurant_id)
            .order_by(Food.id.asc())
            .all()
        )

    def update(
        self,
        food_id: int,
        food_data,
    ):
        food = (
            self.db.query(Food)
            .filter(Food.id == food_id)
            .first()
        )

        if food is None:
            return None

        update_data = food_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(food, field, value)

        self.db.flush()
        self.db.refresh(food)

        return food