from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.food_category import (
    FoodCategoryCreate,
    FoodCategoryUpdate,
)
from models.food_category import FoodCategory
from models.user import User, UserRole
from repositories.food_category_map_repository import (
    FoodCategoryMapRepository,
)
from repositories.food_category_repository import (
    FoodCategoryRepository,
)
from repositories.food_repository import (
    FoodRepository,
)
from repositories.restaurant_repository import (
    RestaurantRepository,
)


class FoodCategoryService:
    def __init__(self, db: Session):
        self.food_category_repository = FoodCategoryRepository(db)

        self.food_category_map_repository = (
            FoodCategoryMapRepository(db)
        )

        self.food_repository = FoodRepository(db)

        self.restaurant_repository = RestaurantRepository(db)

    def create_category(
        self,
        category_data: FoodCategoryCreate,
        current_user: User,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        category = FoodCategory(
            name=category_data.name,
        )

        return self.food_category_repository.create(category)

    def get_category_by_id(
        self,
        category_id: int,
    ):
        category = self.food_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food category not found",
            )

        return category

    def get_all_categories(self):
        return self.food_category_repository.get_all()

    def update_category(
        self,
        category_id: int,
        category_data: FoodCategoryUpdate,
        current_user: User,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        category = self.food_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food category not found",
            )

        return self.food_category_repository.update(
            category_id,
            category_data,
        )

    def delete_category(
        self,
        category_id: int,
        current_user: User,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        category = self.food_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food category not found",
            )

        self.food_category_repository.delete(category)

    def add_categories_to_food(
        self,
        food_id: int,
        category_ids: list[int],
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
                detail="You do not have permission to manage this food",
            )

        category_ids = list(dict.fromkeys(category_ids))

        for category_id in category_ids:
            category = self.food_category_repository.get_by_id(
                category_id
            )

            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Food category {category_id} not found",
                )

            existing_mapping = (
                self.food_category_map_repository
                .get_by_food_and_category(
                    food_id=food_id,
                    category_id=category_id,
                )
            )

            if existing_mapping is None:
                self.food_category_map_repository.add(
                    food_id=food_id,
                    category_id=category_id,
                )

        return self.get_food_categories(food_id)

    def get_food_categories(
        self,
        food_id: int,
    ):
        food = self.food_repository.get_by_id(food_id)

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            )

        mappings = (
            self.food_category_map_repository
            .get_by_food_id(food_id)
        )

        categories = []

        for mapping in mappings:
            category = self.food_category_repository.get_by_id(
                mapping.category_id
            )

            if category is not None:
                categories.append(category)

        return categories

    def remove_category_from_food(
        self,
        food_id: int,
        category_id: int,
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
                detail="You do not have permission to manage this food",
            )

        mapping = (
            self.food_category_map_repository
            .get_by_food_and_category(
                food_id=food_id,
                category_id=category_id,
            )
        )

        if mapping is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food category is not assigned to this food",
            )

        self.food_category_map_repository.delete(mapping)