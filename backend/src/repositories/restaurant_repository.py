from sqlalchemy.orm import Session

from models.restaurant import Restaurant
from repositories.base_repository import BaseRepository
from dto.restaurant import RestaurantUpdate

class RestaurantRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Restaurant)
    def get_all(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None,
    ):
        query = self.db.query(Restaurant)

        if search:
            query = query.filter(Restaurant.name.ilike(f"%{search}%"))

        if is_active is not None:
            query = query.filter(Restaurant.is_active == is_active)

        offset = (page - 1) * page_size

        return query.offset(offset).limit(page_size).all()

    
    def update(
        self,
        restaurant_id: int,
        restaurant_data: RestaurantUpdate,
    ):
        restaurant = (
            self.db.query(Restaurant)
            .filter(Restaurant.id == restaurant_id)
            .first()
        )

        if restaurant is None:
            return None

        update_data = restaurant_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(restaurant, field, value)

        self.db.flush()
        self.db.refresh(restaurant)

        return restaurant