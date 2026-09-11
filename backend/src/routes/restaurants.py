from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import (
    get_current_admin_or_restaurant_owner,
    get_current_restaurant_owner,
)
from dto.food import FoodCreate, FoodResponse
from dto.menu import MenuCreate, MenuResponse
from dto.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from dto.restaurant_category import (
    RestaurantCategoryAssign,
    RestaurantCategoryResponse,
)
from models.user import User
from services.food_service import FoodService
from services.menu_service import MenuService
from services.restaurant_category_service import RestaurantCategoryService
from services.restaurant_service import RestaurantService
from dto.order import OrderResponse
from services.order_service import OrderService

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)


# Create a new restaurant. Only accessible to authenticated users with the
# RESTAURANT_OWNER role; the new restaurant is linked to the current owner's id.
@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_owner: Annotated[
        User,
        Depends(get_current_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)
    try: 
        restaurant = restaurant_service.create_restaurant(
            restaurant_data=restaurant_data,
            owner_id=current_owner.id,
        )

        db.commit()
        return restaurant
    
    except Exception:
        db.rollback()
        raise


# List restaurants with pagination, optional text search, and an optional
# is_active filter. Public endpoint, no authentication required.
@router.get(
    "/",
    response_model=list[RestaurantResponse],
)
def get_restaurants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)

    return restaurant_service.get_all_restaurants(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
    )


# Get a single restaurant by its id. Public endpoint. Returns 404 if no
# restaurant exists with the given id.
@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)

    restaurant = restaurant_service.get_restaurant_by_id(restaurant_id)

    if restaurant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return restaurant


# Partially update a restaurant's fields. Accessible to an admin or the
# restaurant's owner.
@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
)
def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)
    try: 
        restaurant = restaurant_service.update_restaurant(
            restaurant_id,
            restaurant_data,
            current_user
        )

        db.commit()

        return restaurant
    except Exception:
        db.rollback()
        raise


# Delete a restaurant by id. Accessible to an admin or the restaurant's
# owner. Returns 204 with no content on success.
@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_restaurant(
    restaurant_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    restaurant_service = RestaurantService(db)
    try: 
        restaurant_service.delete_restaurant(
            restaurant_id,
            current_user,
        )

        db.commit()
    except Exception:
        db.rollback()
        raise



# Create a new menu under a specific restaurant. Only accessible to
# authenticated users with the RESTAURANT_OWNER role.
@router.post(
    "/{restaurant_id}/menus",
    response_model=MenuResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_menu(
    restaurant_id: int,
    menu_data: MenuCreate,
    current_user: Annotated[
        User,
        Depends(get_current_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    menu_service = MenuService(db)

    try:

        menu = menu_service.create_menu(
            restaurant_id=restaurant_id,
            menu_data=menu_data,
            user_id=current_user.id,
        )

        db.commit()

        return menu

    except Exception:
        db.rollback()
        raise


# List all menus belonging to a specific restaurant. Public endpoint.
@router.get(
    "/{restaurant_id}/menus",
    response_model=list[MenuResponse],
)
def get_restaurant_menus(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    menu_service = MenuService(db)

    return menu_service.get_restaurant_menus(
        restaurant_id=restaurant_id,
    )


# List all categories assigned to a specific restaurant. Public endpoint.
@router.get(
    "/{restaurant_id}/categories",
    response_model=list[RestaurantCategoryResponse],
)
def get_restaurant_categories(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

    return category_service.get_restaurant_categories(
        restaurant_id=restaurant_id,
    )


# Assign one or more categories to a restaurant. Accessible to an admin or
# the restaurant's owner. Returns the restaurant's updated category list.
@router.post(
    "/{restaurant_id}/categories",
    response_model=list[RestaurantCategoryResponse],
    status_code=status.HTTP_200_OK,
)
def add_categories_to_restaurant(
    restaurant_id: int,
    category_data: RestaurantCategoryAssign,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

    try:
        categories = category_service.add_categories_to_restaurant(
            restaurant_id=restaurant_id,
            category_ids=category_data.category_ids,
            current_user=current_user,
        )

        db.commit()

        return categories

    except Exception:
        db.rollback()
        raise


# Remove a single category from a restaurant. Accessible to an admin or the
# restaurant's owner. Returns 204 with no content on success.
@router.delete(
    "/{restaurant_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_category_from_restaurant(
    restaurant_id: int,
    category_id: int,
    current_user: Annotated[
        User,
        Depends(get_current_admin_or_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    category_service = RestaurantCategoryService(db)

    try:
        category_service.remove_category_from_restaurant(
            restaurant_id=restaurant_id,
            category_id=category_id,
            current_user=current_user,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise



# Create a new food item under a specific restaurant. Only accessible to
# authenticated users with the RESTAURANT_OWNER role.
@router.post(
    "/{restaurant_id}/foods",
    response_model=FoodResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_food(
    restaurant_id: int,
    food_data: FoodCreate,
    current_user: Annotated[
        User,
        Depends(get_current_restaurant_owner),
    ],
    db: Session = Depends(get_db),
):
    food_service = FoodService(db)

    try:
        food = food_service.create_food(
            restaurant_id=restaurant_id,
            food_data=food_data,
            current_user=current_user,
        )

        db.commit()

        return food

    except Exception:
        db.rollback()
        raise


# List all food items belonging to a specific restaurant. Public endpoint.
@router.get(
    "/{restaurant_id}/foods",
    response_model=list[FoodResponse],
)
def get_restaurant_foods(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    food_service = FoodService(db)

    return food_service.get_restaurant_foods(
        restaurant_id=restaurant_id,
    )

@router.get(
    "/{restaurant_id}/orders",
    response_model=list[OrderResponse],
)
def get_restaurant_orders(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Annotated[
        User,
        Depends(get_current_restaurant_owner),
    ] = None,
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    return order_service.get_restaurant_orders(
        restaurant_id=restaurant_id,
        owner_id=current_user.id,
        page=page,
        limit=limit,
    )