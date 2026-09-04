from sqlalchemy.orm import Session

from models.food_category_map import FoodCategoryMap


class FoodCategoryMapRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        food_id: int,
        category_id: int,
    ):
        mapping = FoodCategoryMap(
            food_id=food_id,
            category_id=category_id,
        )

        self.db.add(mapping)
        self.db.flush()

        return mapping

    def get_by_food_id(
        self,
        food_id: int,
    ):
        return (
            self.db.query(FoodCategoryMap)
            .filter(
                FoodCategoryMap.food_id == food_id
            )
            .all()
        )

    def get_by_food_and_category(
        self,
        food_id: int,
        category_id: int,
    ):
        return (
            self.db.query(FoodCategoryMap)
            .filter(
                FoodCategoryMap.food_id == food_id,
                FoodCategoryMap.category_id == category_id,
            )
            .first()
        )

    def delete(self, mapping: FoodCategoryMap):
        self.db.delete(mapping)
        self.db.flush()