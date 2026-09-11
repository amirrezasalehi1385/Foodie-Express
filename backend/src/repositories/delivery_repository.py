from sqlalchemy.orm import Session

from models.delivery import Delivery, DeliveryStatus


class DeliveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: int,
        delivery_man_id: int,
    ):
        delivery = Delivery(
            order_id=order_id,
            delivery_man_id=delivery_man_id,
        )

        self.db.add(delivery)
        self.db.flush()

        return delivery

    def get_by_id(
        self,
        delivery_id: int,
    ):
        return (
            self.db.query(Delivery)
            .filter(
                Delivery.id == delivery_id
            )
            .first()
        )

    def get_by_order_id(
        self,
        order_id: int,
    ):
        return (
            self.db.query(Delivery)
            .filter(
                Delivery.order_id == order_id
            )
            .first()
        )

    def get_by_delivery_man_id(
        self,
        delivery_man_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Delivery)
            .filter(
                Delivery.delivery_man_id == delivery_man_id
            )
            .order_by(Delivery.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update(self, delivery: Delivery):
        self.db.add(delivery)
        self.db.flush()

        return delivery