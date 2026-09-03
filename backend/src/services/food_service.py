from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.food import FoodCreate, FoodUpdate
from models.food import Food
from models.user import User, UserRole
from repositories.food_repository import FoodRepository
from repositories.restaurant_repository import RestaurantRepository


class FoodService:
    def __init__(self, db: Session):
        self.food_repository = FoodRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def create_food(
        self,
        restaurant_id: int,
        food_data: FoodCreate,
        current_user: User,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if restaurant.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to add food to this restaurant",
            )

        food = Food(
            restaurant_id=restaurant_id,
            name=food_data.name,
            description=food_data.description,
            price=food_data.price,
            image_url=food_data.image_url,
            is_available=food_data.is_available,
            preparation_time_minutes=food_data.preparation_time_minutes,
        )

        return self.food_repository.create(food)

    def get_restaurant_foods(
        self,
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

        return self.food_repository.get_by_restaurant_id(
            restaurant_id
        )

    def get_food_by_id(
        self,
        food_id: int,
    ):
        food = self.food_repository.get_by_id(food_id)

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            )

        return food

    def update_food(
        self,
        food_id: int,
        food_data: FoodUpdate,
        current_user: User,
    ):
        food = self.food_repository.get_by_id(food_id)

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            )

        restaurant = self.restaurant_repository.get_by_id(
            food.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this food",
            )

        return self.food_repository.update(
            food_id,
            food_data,
        )

    def delete_food(
        self,
        food_id: int,
        current_user: User,
    ):
        food = self.food_repository.get_by_id(food_id)

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            )

        restaurant = self.restaurant_repository.get_by_id(
            food.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this food",
            )

        self.food_repository.delete(food)