from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class AddressCreate(BaseModel):
    title: str
    recipient_name: str
    phone: str

    province: str | None = None
    city: str | None = None
    address: str
    postal_code: str | None = None

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    is_default: bool = False

class AddressUpdate(BaseModel):
    title: str | None = None
    recipient_name: str | None = None
    phone: str | None = None

    province: str | None = None
    city: str | None = None
    address: str | None = None
    postal_code: str | None = None

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    is_default: bool | None = None

class AddressResponse(BaseModel):
    id: int
    user_id: int

    title: str
    recipient_name: str
    phone: str

    province: str | None
    city: str | None
    address: str
    postal_code: str | None

    latitude: Decimal | None
    longitude: Decimal | None

    is_default: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)