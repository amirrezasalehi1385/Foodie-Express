from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.order import OrderStatus


class OrderStatusHistoryResponse(BaseModel):
    id: int
    status: OrderStatus
    changed_by: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
