from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.menu import MenuCreate, MenuUpdate
from models.menu import Menu
from models.user import UserRole, User
from repositories.menu_repository import MenuRepository
from repositories.restaurant_repository import RestaurantRepository
from services.user_service import UserService


class MenuService:
    def __init__(self, db: Session):
        self.menu_repository = MenuRepository(db)
        self.restaurant_repository = RestaurantRepository(db)

    def create_menu(
        self,
        restaurant_id: int,
        menu_data: MenuCreate,
        user_id: int,
    ):
        restaurant = self.restaurant_repository.get_by_id(
            restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if restaurant.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to create a menu for this restaurant",
            )

        menu = Menu(
            restaurant_id=restaurant_id,
            name=menu_data.name,
            display_order=menu_data.display_order,
            is_active=menu_data.is_active,
        )

        return self.menu_repository.create(menu)

    def get_restaurant_menus(
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

        return self.menu_repository.get_by_restaurant_id(
            restaurant_id
        )

    def get_menu_by_id(
        self,
        menu_id: int,
    ):
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        return menu

    def update_menu(
        self,
        menu_id: int,
        menu_data: MenuUpdate,
        current_user: User,
    ):
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        restaurant = self.restaurant_repository.get_by_id(
            menu.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if (
            restaurant.owner_id != current_user.id
            and current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this menu",
            )

        return self.menu_repository.update(
            menu_id,
            menu_data,
        )

    def delete_menu(
        self,
        menu_id: int,
        current_user: User,
    ):
        menu = self.menu_repository.get_by_id(menu_id)

        if menu is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found",
            )

        restaurant = self.restaurant_repository.get_by_id(
            menu.restaurant_id
        )

        if restaurant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        if (
            restaurant.owner_id != current_user.id
            and current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this menu",
            )

        self.menu_repository.delete(menu)