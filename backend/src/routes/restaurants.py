from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from dependencies.auth import get_current_restaurant_owner
from config.database import get_db
from dependencies.auth import get_current_user
from dto.restaurant import RestaurantCreate, RestaurantResponse
from models.user import User, UserRole
from services.restaurant_service import RestaurantService


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
)


@router.post(
    "",
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

    restaurant = restaurant_service.create_restaurant(
        restaurant_data=restaurant_data,
        owner_id=current_owner.id,
    )

    db.commit()

    return restaurant