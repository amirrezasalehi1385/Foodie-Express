from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.restaurant_category import (
    RestaurantCategoryCreate,
    RestaurantCategoryUpdate,
)
from models.restaurant_category import RestaurantCategory
from models.user import User, UserRole
from repositories.restaurant_category_map_repository import (
    RestaurantCategoryMapRepository,
)
from repositories.restaurant_category_repository import (
    RestaurantCategoryRepository,
)
from repositories.restaurant_repository import RestaurantRepository


class RestaurantCategoryService:
    def __init__(self, db: Session):
        self.restaurant_category_repository = (
            RestaurantCategoryRepository(db)
        )

        self.restaurant_category_map_repository = (
            RestaurantCategoryMapRepository(db)
        )

        self.restaurant_repository = RestaurantRepository(db)

    def create_category(
        self,
        category_data: RestaurantCategoryCreate,
        current_user: User,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        category = RestaurantCategory(
            name=category_data.name,
        )

        return self.restaurant_category_repository.create(category)

    def get_category_by_id(
        self,
        category_id: int,
    ):
        category = self.restaurant_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant category not found",
            )

        return category

    def get_all_categories(self):
        return self.restaurant_category_repository.get_all()

    def update_category(
        self,
        category_id: int,
        category_data: RestaurantCategoryUpdate,
        current_user: User,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        category = self.restaurant_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant category not found",
            )

        return self.restaurant_category_repository.update(
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

        category = self.restaurant_category_repository.get_by_id(
            category_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant category not found",
            )

        self.restaurant_category_repository.delete(category)

    def add_categories_to_restaurant(
        self,
        restaurant_id: int,
        category_ids: list[int],
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

        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage this restaurant",
            )

        # حذف IDهای تکراری، بدون به‌هم‌زدن ترتیب
        category_ids = list(dict.fromkeys(category_ids))

        for category_id in category_ids:

            category = self.restaurant_category_repository.get_by_id(
                category_id
            )

            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Restaurant category {category_id} not found",
                )

            existing_mapping = (
                self.restaurant_category_map_repository
                .get_by_restaurant_and_category(
                    restaurant_id=restaurant_id,
                    category_id=category_id,
                )
            )

            if existing_mapping is None:
                self.restaurant_category_map_repository.add(
                    restaurant_id=restaurant_id,
                    category_id=category_id,
                )

        return self.get_restaurant_categories(
            restaurant_id
        )

    def get_restaurant_categories(
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

        mappings = (
            self.restaurant_category_map_repository
            .get_by_restaurant_id(restaurant_id)
        )

        categories = []

        for mapping in mappings:
            category = self.restaurant_category_repository.get_by_id(
                mapping.category_id
            )

            if category is not None:
                categories.append(category)

        return categories

    def remove_category_from_restaurant(
        self,
        restaurant_id: int,
        category_id: int,
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

        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage this restaurant",
            )

        mapping = (
            self.restaurant_category_map_repository
            .get_by_restaurant_and_category(
                restaurant_id=restaurant_id,
                category_id=category_id,
            )
        )

        if mapping is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category is not assigned to this restaurant",
            )

        self.restaurant_category_map_repository.delete(mapping)