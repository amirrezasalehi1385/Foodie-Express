from models.order import OrderStatus
from models.order_status_history import OrderStatusHistory

from repositories.order_status_history_repository import (
    OrderStatusHistoryRepository,
)


class OrderStatusHistoryService:

    def __init__(self, db):
        self.repository = OrderStatusHistoryRepository(db)

    def create(
        self,
        order_id: int,
        status: OrderStatus,
        changed_by: int | None,
    ) -> OrderStatusHistory:

        return self.repository.create(
            order_id=order_id,
            status=status,
            changed_by=changed_by,
        )

    def get_by_order_id(
        self,
        order_id: int,
    ) -> list[OrderStatusHistory]:

        return self.repository.get_by_order_id(
            order_id=order_id
        )