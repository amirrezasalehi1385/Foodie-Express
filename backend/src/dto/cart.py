from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from dto.cart_item import CartItemResponse


class CartResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime
    items: list[CartItemResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)