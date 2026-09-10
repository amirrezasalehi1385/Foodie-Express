from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from dto.order import OrderResponse, OrderCreate, OrderStatusUpdate, OrderCancellationRequest
from services.order_service import OrderService



router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    try:
        order = order_service.create_order(
            user_id=current_user.id,
            delivery_address_id=data.delivery_address_id,
            discount_code=data.discount_code
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise

@router.get(
    "",
    response_model=list[OrderResponse],
)
def get_user_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    return order_service.get_user_orders(
        user_id=current_user.id,
        page=page,
        limit=limit,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    return order_service.get_order_by_id(
        user_id=current_user.id,
        order_id=order_id,
    )

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def change_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    try:
        order = order_service.change_order_status(
            current_user = current_user,
            order_id=order_id,
            new_status=data.status,
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise



@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    data: OrderCancellationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_service = OrderService(db)

    try:
        order = order_service.cancel_order(
            user_id=current_user.id,
            order_id=order_id,
            reason=data.reason,
            note=data.note,
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise