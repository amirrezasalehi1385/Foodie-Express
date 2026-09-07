from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from models.payment import PaymentStatus, PaymentMethod


class PaymentConfirmRequest(BaseModel):
    card_number: str = Field(
        min_length=13,
        max_length=19,
    )
    card_holder_name: str | None = None
    expiry_month: int | None = Field(default=None, ge=1, le=12)
    expiry_year: int | None = None
    cvv: str | None = Field(default=None, min_length=3, max_length=4)


class PaymentInitiateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    status: PaymentStatus
    payment_token: str

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    card_last_four: str | None
    receipt_number: str | None
    failure_reason: str | None
    created_at: datetime
    completed_at: datetime | None