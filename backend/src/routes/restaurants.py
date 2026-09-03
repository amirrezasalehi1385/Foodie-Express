from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from dependencies.auth import get_current_restaurant_owner, get_current_admin_or_restaurant_owner
from config.database import get_db
from dependencies.auth import get_current_user
from dto.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from dto.menu import MenuCreate, MenuResponse
from models.user import User, UserRole
from services.restaurant_service import RestaurantService
from services.menu_service import MenuService


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)


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
        )

        db.commit()

        return restaurant
    except Exception:
        db.rollback()
        raise

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
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    return None



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