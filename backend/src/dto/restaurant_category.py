from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCategoryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class RestaurantCategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class RestaurantCategoryResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RestaurantCategoryAssign(BaseModel):
    category_ids: list[int] = Field(
        min_length=1,
    )