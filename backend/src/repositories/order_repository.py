from sqlalchemy.orm import Session

from models.order import Order, OrderStatus

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = 10,
    ):
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, order_id: int):
        return (
            self.db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

    def create(self, order: Order):
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)

        return order

    def update(self, order: Order):
        self.db.commit()
        self.db.refresh(order)

        return order

    def delete(self, order: Order):
        self.db.delete(order)
        self.db.commit()

    def get_by_restaurant_id(self, restaurant_id: int):
        return (
            self.db.query(Order)
            .filter(Order.restaurant_id == restaurant_id)
            .all()
        )
    def get_available_for_delivery(
        self,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Order)
            .filter(Order.status == OrderStatus.READY)
            .order_by(Order.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )