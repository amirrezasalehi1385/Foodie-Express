from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

from models.discount import DiscountType


class DiscountCreateRequest(BaseModel):
    code: str
    type: DiscountType
    value: Decimal
    restaurant_id: int | None = None
    min_order_amount: Decimal | None = None
    max_discount_amount: Decimal | None = None
    usage_limit: int | None = None
    usage_limit_per_user: int | None = 1
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    @model_validator(mode="after")
    def validate_value_range(self):
        if self.type == DiscountType.PERCENTAGE and not (0 < self.value <= 100):
            raise ValueError("Percentage discount value must be between 0 and 100")
        if self.type == DiscountType.FIXED_AMOUNT and self.value <= 0:
            raise ValueError("Fixed discount amount must be greater than 0")
        return self


class DiscountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    type: DiscountType
    value: Decimal
    restaurant_id: int | None
    min_order_amount: Decimal | None
    max_discount_amount: Decimal | None
    usage_limit: int | None
    usage_limit_per_user: int | None
    valid_from: datetime | None
    valid_until: datetime | None
    is_active: bool
    created_at: datetime


class DiscountPreviewRequest(BaseModel):
    code: str
    restaurant_id: int
    subtotal: Decimal


class DiscountPreviewResponse(BaseModel):
    discount_amount: Decimal