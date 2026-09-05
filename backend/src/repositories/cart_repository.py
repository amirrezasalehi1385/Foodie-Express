from sqlalchemy.orm import Session

from models.cart import Cart


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int):
        return (
            self.db.query(Cart)
            .filter(Cart.user_id == user_id)
            .first()
        )

    def get_by_id(self, cart_id: int):
        return (
            self.db.query(Cart)
            .filter(Cart.id == cart_id)
            .first()
        )

    def create(self, user_id: int, restaurant_id: int):
        cart = Cart(
            user_id=user_id,
            restaurant_id=restaurant_id,
        )

        self.db.add(cart)
        self.db.flush()

        return cart

    def delete(self, cart: Cart):
        self.db.delete(cart)
        self.db.flush()