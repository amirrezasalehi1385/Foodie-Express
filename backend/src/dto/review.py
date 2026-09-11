from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    order_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdateRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    user_id: int
    restaurant_id: int
    rating: int
    comment: str | None
    created_at: datetime
    updated_at: datetime


class RestaurantRatingSummaryResponse(BaseModel):
    average_rating: float
    review_count: int