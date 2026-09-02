from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    phone: str = Field(
        pattern=r"^09\d{9}$"
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None