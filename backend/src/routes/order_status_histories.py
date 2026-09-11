from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user, get_db
from dto.order_status_history import (
    OrderStatusHistoryResponse,
)
from services.order_status_history_service import (
    OrderStatusHistoryService,
)

router = APIRouter(
    prefix="/orders",
    tags=["Order Status History"],
)


@router.get(
    "/{order_id}/status-history",
    response_model=list[OrderStatusHistoryResponse],
)
def get_order_status_history(
    order_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    service = OrderStatusHistoryService(db)

    return service.get_by_order_id(order_id)