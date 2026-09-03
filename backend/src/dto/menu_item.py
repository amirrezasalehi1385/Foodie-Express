from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    display_order: int = Field(default=0, ge=0)


class MenuItemResponse(BaseModel):
    menu_id: int
    food_id: int
    display_order: int

    model_config = ConfigDict(from_attributes=True)