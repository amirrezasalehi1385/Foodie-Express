from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dto.restaurant import RestaurantCreate, RestaurantUpdate
from models.restaurant import Restaurant, RestaurantStatus
from repositories.restaurant_repository import RestaurantRepository
from models.user import User, UserRole

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

    def get_all_restaurants(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        is_active: bool | None = None,
    ):
        return self.restaurant_repository.get_all(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
        )

    
    def get_restaurant_by_id(self, restaurant_id : int): 
        return self.restaurant_repository.get_by_id(restaurant_id)


    def update_restaurant(
        self,
        restaurant_id: int,
        restaurant_data: RestaurantUpdate,
    ):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        return self.restaurant_repository.update(
            restaurant_id,
            restaurant_data,
        )

    def delete_restaurant(
        self,
        restaurant_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        self.restaurant_repository.delete(restaurant)