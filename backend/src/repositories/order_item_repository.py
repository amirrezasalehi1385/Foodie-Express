from sqlalchemy.orm import Session

from models.order_items import OrderItem


class OrderItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_item_id: int):
        return (
            self.db.query(OrderItem)
            .filter(OrderItem.id == order_item_id)
            .first()
        )

    def get_by_order_id(self, order_id: int):
        return (
            self.db.query(OrderItem)
            .filter(OrderItem.order_id == order_id)
            .all()
        )

    def create(
        self,
        order_item: OrderItem,
    ):
        self.db.add(order_item)
        self.db.flush()

        return order_item