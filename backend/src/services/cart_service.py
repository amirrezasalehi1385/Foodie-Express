from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User
from repositories.cart_repository import (
    CartRepository
)
from repositories.food_repository import FoodRepository
from repositories.cart_item_repository import CartItemRepository
from services.user_service import UserService
from dto.cart import CartResponse

class CartService:
    def __init__(self, db: Session):
        self.cart_repository = CartRepository(db)
        self.cart_item_repository = CartItemRepository(db)
        self.food_repository = FoodRepository(db)

    def get_cart(
        self,
        user_id: int
    ):
        cart = self.cart_repository.get_by_user_id(user_id=user_id)

        if cart is None : 
            raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="Cart not found",
                        )
        
        return cart
    def add_to_cart(
            self,
            user_id: int,
            food_id: int,
            quantity: int
    ): 
        food = self.food_repository.get_by_id(food_id)

        if food is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found",
            ) 

        if food.is_available == False : 
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Food is not available"
            ) 
            
        cart = self.cart_repository.get_by_user_id(user_id=user_id)

        if cart is None :
            cart = self.cart_repository.create(user_id=user_id, restaurant_id=food.restaurant_id)

        if  cart.restaurant_id != food.restaurant_id : 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart contains items from another restaurant"
            )

        cart_item  = self.cart_item_repository.get_by_cart_and_food(cart_id=cart.id, food_id=food_id)

        if cart_item is None : 
            self.cart_item_repository.create(cart_id=cart.id, food_id=food_id, quantity=quantity)
            return cart 

        existing_quantity = cart_item.quantity
        new_quantity = existing_quantity + quantity
        self.cart_item_repository.update(cart_item=cart_item, quantity=new_quantity)

        return cart
    def update_cart_item(
            self,
            user_id: int,
            cart_item_id : int,
            quantity: int
    ): 
        cart = self.cart_repository.get_by_user_id(user_id=user_id)

        if cart is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        cart_item = self.cart_item_repository.get_by_id(cart_item_id)

        if cart_item is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        if cart_item.cart_id != cart.id : 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart item doesn't doesn't belong to user cart"
            )

        self.cart_item_repository.update(cart_item=cart_item, quantity=quantity)

        return cart
    # TODO: optimize clear_cart by adding a bulk delete_by_cart_id
    # to CartItemRepository instead of deleting items one by one.
    def remove_cart_item(
        self,
        user_id : int,
        cart_item_id : int
    ): 
        cart = self.cart_repository.get_by_user_id(user_id=user_id)

        if cart is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        cart_item = self.cart_item_repository.get_by_id(cart_item_id)

        if cart_item is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        if not cart_item.cart_id == cart.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        self.cart_item_repository.delete(cart_item=cart_item)

        return cart

    def clear_cart(
            self,
            user_id: int
    ): 
        cart = self.cart_repository.get_by_user_id(user_id=user_id)

        if cart is None : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )

        cart_items = self.cart_item_repository.get_by_cart_id(cart_id=cart.id)

        for cart_item in cart_items:
            self.remove_cart_item(
                user_id=user_id,
                cart_item_id=cart_item.id
            )

        return cart




        

        


