from sqlalchemy.orm import Session

from dto.restaurant import RestaurantCreate
from models.restaurant import Restaurant, RestaurantStatus
from repositories.restaurant_repository import RestaurantRepository


class RestaurantService:
    def __init__(self, db: Session):
        self.restaurant_repository = RestaurantRepository(db)

    def create_restaurant(
        self,
        restaurant_data: RestaurantCreate,
        owner_id: int,
    ) -> Restaurant:

        restaurant = Restaurant(
            owner_id=owner_id,
            name=restaurant_data.name,
            description=restaurant_data.description,
            phone=restaurant_data.phone,
            address=restaurant_data.address,
            latitude=restaurant_data.latitude,
            longitude=restaurant_data.longitude,
            logo_url=restaurant_data.logo_url,
            cover_image_url=restaurant_data.cover_image_url,
            status=RestaurantStatus.PENDING,
        )

        return self.restaurant_repository.create(restaurant)