from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.restaurant import RestaurantCreate, RestaurantUpdate
from models.restaurant import Restaurant, RestaurantStatus
from models.user import User, UserRole
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




from repositories.admin_actions_log_repository import AdminActionLogRepository


class RestaurantService:
    def __init__(self, db: Session):
        self.restaurant_repository = RestaurantRepository(db)
        self.admin_action_log_repository = AdminActionLogRepository(db)

    ...

    from repositories.admin_actions_log_repository import AdminActionLogRepository


class RestaurantService:
    def __init__(self, db: Session):
        self.restaurant_repository = RestaurantRepository(db)
        self.admin_action_log_repository = AdminActionLogRepository(db)


    def update_restaurant(
        self,
        restaurant_id: int,
        restaurant_data: RestaurantUpdate,
        current_user: User,
    ):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

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
                detail="You do not have permission to update this restaurant",
            )

        updated_restaurant = self.restaurant_repository.update(
            restaurant_id,
            restaurant_data,
        )

        if current_user.role == UserRole.ADMIN and restaurant.owner_id != current_user.id:
            changed_fields = ", ".join(
                restaurant_data.model_dump(exclude_unset=True).keys()
            )

            self.admin_action_log_repository.create(
                admin_id=current_user.id,
                action="UPDATE_RESTAURANT",
                target_type="restaurant",
                target_id=restaurant.id,
                description=f"Updated fields: {changed_fields}",
            )

        return updated_restaurant

    def delete_restaurant(
        self,
        restaurant_id: int,
        current_user: User,
    ):
        restaurant = self.restaurant_repository.get_by_id(restaurant_id)

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
                detail="You do not have permission to delete this restaurant",
            )

        if current_user.role == UserRole.ADMIN and restaurant.owner_id != current_user.id:
            self.admin_action_log_repository.create(
                admin_id=current_user.id,
                action="DELETE_RESTAURANT",
                target_type="restaurant",
                target_id=restaurant.id,
                description=f"Deleted restaurant '{restaurant.name}'",
            )

        self.restaurant_repository.delete(restaurant)

    def get_my_restaurants(self, user_id: int):
        return self.restaurant_repository.get_by_owner_id(user_id)

    def get_by_id_and_owner(
            self,
            restaurant_id: int,
            owner_id: int,
    ):
        return (
            self.db.query(Restaurant)
            .filter(
                Restaurant.id == restaurant_id,
                Restaurant.owner_id == owner_id,
            )
            .first()
        )