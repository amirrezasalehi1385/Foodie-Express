from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.delivery import DeliveryStatus


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    delivery_man_id: int
    status: DeliveryStatus
    picked_up_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime
    updated_at: datetime