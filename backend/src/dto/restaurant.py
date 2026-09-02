from pydantic import BaseModel, Field
from models.restaurant import RestaurantStatus
from decimal import Decimal


class RestaurantCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    address: str | None = Field(
        default=None,
        max_length=5000,
    )

    latitude: float | None = None
    longitude: float | None = None

    logo_url: str | None = Field(
        default=None,
        max_length=500,
    )

    cover_image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class RestaurantResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    phone: str | None
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    logo_url: str | None
    cover_image_url: str | None
    status: RestaurantStatus
    average_rating: Decimal
    rating_count: int

    model_config = {
        "from_attributes": True
    }