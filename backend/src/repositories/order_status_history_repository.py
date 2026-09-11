from sqlalchemy.orm import Session

from models.order_status_history import OrderStatusHistory


class OrderStatusHistoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: int,
        status,
        changed_by: int | None,
    ) -> OrderStatusHistory:

        history = OrderStatusHistory(
            order_id=order_id,
            status=status,
            changed_by=changed_by,
        )

        self.db.add(history)
        self.db.flush()

        return history

    def get_by_order_id(
        self,
        order_id: int,
    ) -> list[OrderStatusHistory]:

        return (
            self.db.query(OrderStatusHistory)
            .filter(
                OrderStatusHistory.order_id == order_id
            )
            .order_by(
                OrderStatusHistory.created_at.asc()
            )
            .all()
        )