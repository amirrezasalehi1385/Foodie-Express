from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CartItemCreate(BaseModel):
    food_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    food_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)