
from pydantic import BaseModel, EmailStr, Field

from models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=20
    )

    email: EmailStr | None = None

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr | None
    role: str
    status: str
    profile_image_url: str | None

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None
    profile_image_url: str | None = Field(
        default=None,
        max_length=500,
    )

class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=20,
        pattern=r"^09\d{9}$",
    )

    email: EmailStr | None = None

    role: UserRole | None = None

    status: UserStatus | None = None

    profile_image_url: str | None = Field(
        default=None,
        max_length=500,
    )