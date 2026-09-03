from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MenuCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    display_order: int = Field(
        default=0,
        ge=0,
    )

    is_active: bool = True


class MenuUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    display_order: int | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None


class MenuResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )