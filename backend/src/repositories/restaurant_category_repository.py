from sqlalchemy.orm import Session

from dto.restaurant_category import RestaurantCategoryUpdate
from models.restaurant_category import RestaurantCategory
from repositories.base_repository import BaseRepository


class RestaurantCategoryRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, RestaurantCategory)

    def update(
        self,
        category_id: int,
        category_data: RestaurantCategoryUpdate,
    ):
        category = (
            self.db.query(RestaurantCategory)
            .filter(RestaurantCategory.id == category_id)
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