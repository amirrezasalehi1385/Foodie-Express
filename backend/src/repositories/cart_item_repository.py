from sqlalchemy.orm import Session

from models.cart_items import CartItem


class CartItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: int):
        return (
            self.db.query(CartItem)
            .filter(CartItem.id == item_id)
            .first()
        )

    def get_by_cart_id(self, cart_id: int):
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id)
            .all()
        )

    def get_by_cart_and_food(
        self,
        cart_id: int,
        food_id: int,
    ):
        return (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.food_id == food_id,
            )
            .first()
        )

    def create(
        self,
        cart_id: int,
        food_id: int,
        quantity: int,
    ):
        cart_item = CartItem(
            cart_id=cart_id,
            food_id=food_id,
            quantity=quantity,
        )

        self.db.add(cart_item)
        self.db.flush()

        return cart_item

    def update(
        self,
        cart_item: CartItem,
        quantity: int,
    ):
        cart_item.quantity = quantity

        self.db.flush()

        return cart_item

    def delete(self, cart_item: CartItem):
        self.db.delete(cart_item)
        self.db.flush()
        