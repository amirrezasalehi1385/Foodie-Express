from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.order import OrderStatus
from models.user import User, UserRole
from models.delivery import Delivery, DeliveryStatus

from repositories.delivery_repository import DeliveryRepository
from repositories.order_repository import OrderRepository

class DeliveryService:
    def __init__(self, db: Session):
        self.delivery_repository = DeliveryRepository(db)
        self.order_repository = OrderRepository(db)

    def claim_order(
        self,
        current_user: User,
        order_id: int,
    ):
        
        order = self.order_repository.get_by_id(order_id=order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.status != OrderStatus.READY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not ready for delivery",
            )

        existing = self.delivery_repository.get_by_order_id(
            order_id=order.id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Order has already been claimed",
            )

        delivery = self.delivery_repository.create(
            order_id=order.id,
            delivery_man_id=current_user.id,
        )

        order.status = OrderStatus.ASSIGNED
        self.order_repository.update(order)

        self.order_status_history_repository.create(
            order_id=order.id,
            status=OrderStatus.ASSIGNED,
            changed_by=current_user.id,
        )

        return delivery

    def get_delivery_by_order_id(
        self,
        order_id: int,
    ):
        delivery = self.delivery_repository.get_by_order_id(
            order_id=order_id,
        )

        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Delivery not found for this order",
            )

        return delivery

    def get_my_deliveries(
        self,
        delivery_man_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        offset = (page - 1) * limit

        return self.delivery_repository.get_by_delivery_man_id(
            delivery_man_id=delivery_man_id,
            offset=offset,
            limit=limit,
        )

    def mark_picked_up(
        self,
        delivery: Delivery,
    ):
        delivery.status = DeliveryStatus.PICKED_UP
        delivery.picked_up_at = datetime.now(timezone.utc)

        self.delivery_repository.update(delivery)

        return delivery

    def mark_delivered(
        self,
        delivery: Delivery,
    ):
        delivery.status = DeliveryStatus.DELIVERED
        delivery.delivered_at = datetime.now(timezone.utc)

        self.delivery_repository.update(delivery)

        return delivery