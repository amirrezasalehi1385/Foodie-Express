from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from config.settings import settings


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str



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

