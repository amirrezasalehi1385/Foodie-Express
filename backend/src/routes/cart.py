from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from dto.cart import CartResponse
from dto.cart_item import CartItemCreate, CartItemUpdate
from models.user import User
from services.cart_service import (
    CartService,
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    cart_service = CartService(db)

    return cart_service.get_cart(
        user_id=current_user.id
    )

@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def add_to_cart(
    data: CartItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    cart_service = CartService(db)


    try:

        cart = cart_service.add_to_cart(
            user_id=current_user.id,
            food_id=data.food_id,
            quantity=data.quantity,
        )

        db.commit()

        return cart

    except Exception:
        db.rollback()
        raise

@router.patch(
    "/items/{cart_item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def update_cart_item(
    data: CartItemUpdate,
    cart_item_id : int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
): 

    cart_service = CartService(db)

    try:

        cart = cart_service.update_cart_item(
            user_id=current_user.id,
            cart_item_id=cart_item_id,
            quantity=data.quantity,
        )

        db.commit()

        return cart

    except Exception:
        db.rollback()
        raise

@router.delete(
    "/items/{cart_item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def delete_cart_item(
    cart_item_id : int, 
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
): 
    cart_service = CartService(db)
    try:

        cart = cart_service.remove_cart_item(
            user_id=current_user.id,
            cart_item_id=cart_item_id,
        )

        db.commit()

        return cart

    except Exception:
        db.rollback()
        raise

@router.delete(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def delete_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) : 
    
    cart_service = CartService(db)

    try:

        cart = cart_service.clear_cart(
            user_id=current_user.id,
        )

        db.commit()

        return cart
    
    except Exception:
        db.rollback()
        raise