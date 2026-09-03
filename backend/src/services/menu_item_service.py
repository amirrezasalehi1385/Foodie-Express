from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.menu_item import MenuItemCreate
from models.menu_item import MenuItem
from models.user import User, UserRole
from repositories.menu_item_repository import MenuItemRepository
from repositories.menu_repository import MenuRepository
from repositories.food_repository import FoodRepository
from repositories.restaurant_repository import RestaurantRepository


class MenuItemService:
    def __init__(self, db: Session):
        self.menu_item_repository = MenuItemRepository(db)
        self.menu_repository = MenuRepository(db)
        self.food_repository = FoodRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def add_food_to_menu(
        self,
        menu_id: int,
        food_id: int,
        menu_item_data: MenuItemCreate,
        current_user: User,
    ):
        # Check if the menu exists
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        # Check if the food exists
        food = self.food_repository.get_by_id(food_id)

        if food is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            )

        # Ensure the food belongs to the same restaurant
        if menu.restaurant_id != food.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Food does not belong to this restaurant",
            )

        # Get the restaurant
        restaurant = self.restaurant_repository.get_by_id(
            menu.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        # Check user permissions
        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage this menu",
            )

        # Prevent duplicate food assignments
        existing_item = (
            self.menu_item_repository.get_by_menu_and_food(
                menu_id=menu_id,
                food_id=food_id,
            )
        )

        if existing_item is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Food is already assigned to this menu",
            )

        # Create the menu item
        return self.menu_item_repository.add(
            menu_id=menu_id,
            food_id=food_id,
            display_order=menu_item_data.display_order,
        )

    def remove_food_from_menu(
        self,
        menu_id: int,
        food_id: int,
        current_user: User,
    ):
        # Check if the menu exists
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        # Get the restaurant
        restaurant = self.restaurant_repository.get_by_id(
            menu.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        # Check user permissions
        if (
            current_user.role != UserRole.ADMIN
            and restaurant.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to manage this menu",
            )

        # Find the menu item
        menu_item = (
            self.menu_item_repository.get_by_menu_and_food(
                menu_id=menu_id,
                food_id=food_id,
            )
        )

        if menu_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food is not assigned to this menu",
            )

        # Delete the menu item
        self.menu_item_repository.delete(menu_item)

    def get_menu_items(self, menu_id: int):
        # Check if the menu exists
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        return self.menu_item_repository.get_by_menu_id(menu_id)