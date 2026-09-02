from sqlalchemy.orm import Session

from models.restaurant import Restaurant
from repositories.base_repository import BaseRepository


class RestaurantRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Restaurant)