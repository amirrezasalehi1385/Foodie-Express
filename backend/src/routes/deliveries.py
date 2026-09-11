from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.order import OrderStatus
from dto.delivery import DeliveryResponse
from dto.order import OrderResponse
from services.delivery_service import DeliveryService
from services.order_service import OrderService


router = APIRouter(
    tags=["Delivery"],
)


@router.get(
    "/orders/available",
    response_model=list[OrderResponse],
)
def get_available_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    return order_service.get_available_orders(
        current_user=current_user,
        page=page,
        limit=limit,
    )


@router.post(
    "/orders/{order_id}/claim",
    response_model=DeliveryResponse,
    status_code=status.HTTP_201_CREATED,
)
def claim_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery_service = DeliveryService(db)

    try:
        delivery = delivery_service.claim_order(
            current_user=current_user,
            order_id=order_id,
        )

        db.commit()
        db.refresh(delivery)

        return delivery

    except Exception:
        db.rollback()
        raise


@router.get(
    "/deliveries/{order_id}",
    response_model=DeliveryResponse,
)
def get_delivery_by_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery_service = DeliveryService(db)

    return delivery_service.get_delivery_by_order_id(
        order_id=order_id,
    )


@router.get(
    "/users/me/deliveries",
    response_model=list[DeliveryResponse],
)
def get_my_deliveries(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delivery_service = DeliveryService(db)

    return delivery_service.get_my_deliveries(
        delivery_man_id=current_user.id,
        page=page,
        limit=limit,
    )