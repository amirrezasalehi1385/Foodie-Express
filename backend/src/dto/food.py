from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FoodCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )

    is_available: bool = True

    preparation_time_minutes: int = Field(
        ge=0,
    )


class FoodUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )

    is_available: bool | None = None

    preparation_time_minutes: int | None = Field(
        default=None,
        ge=0,
    )


class FoodResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None
    price: Decimal
    image_url: str | None
    is_available: bool
    preparation_time_minutes: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )