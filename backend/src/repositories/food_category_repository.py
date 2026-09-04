from sqlalchemy.orm import Session

from dto.food_category import FoodCategoryUpdate
from models.food_category import FoodCategory
from repositories.base_repository import BaseRepository


class FoodCategoryRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, FoodCategory)

    def update(
        self,
        category_id: int,
        category_data: FoodCategoryUpdate,
    ):
        category = (
            self.db.query(FoodCategory)
            .filter(FoodCategory.id == category_id)
            .first()
        )

        if category is None:
            return None

        update_data = category_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(category, field, value)

        self.db.flush()
        self.db.refresh(category)

        return category