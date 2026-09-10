from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from models.order import OrderStatus
from models.cancelation_reason import CancellationReason


class OrderCreate(BaseModel):
    delivery_address_id: int
    discount_code: str | None = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemResponse(BaseModel):
    id: int
    food_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    delivery_address_id: int
    discount_id: int | None

    subtotal: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    status: OrderStatus
    cancellation_reason: str | None

    created_at: datetime
    updated_at: datetime

    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class OrderCancellationRequest(BaseModel):
    reason: CancellationReason
    note: str | None = None