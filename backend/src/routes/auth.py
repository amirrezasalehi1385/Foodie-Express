from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from dto.auth import LoginRequest, TokenResponse
from dto.user import UserCreate, UserResponse
from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# Register a new user account. Public endpoint. Raises 409 if a user with
# the given identifier (e.g. phone/email) already exists.
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        user = auth_service.register(user_data)

        db.commit()

        return user

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# Authenticate a user with phone and password, returning a bearer access
# token and a refresh token. Public endpoint. Raises 401 if credentials
# are invalid.
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        access_token, refresh_token = auth_service.login(
            phone=login_data.phone,
            password=login_data.password,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

from dto.auth import LoginRequest, RefreshRequest, TokenResponse


# Exchange a valid, unrevoked refresh token for a new access/refresh
# token pair (rotation). Public endpoint. Raises 401 if the refresh
# token is invalid, expired, or already used.
@router.post(
    "/token/refresh",
    response_model=TokenResponse,
)
def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        access_token, new_refresh_token = auth_service.refresh(
            refresh_token=refresh_data.refresh_token,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


# Revoke a refresh token so it can no longer be used. Public endpoint
# (no access token required — logging out with just the refresh token
# is fine since it's already the credential being revoked).
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        auth_service.logout(refresh_token=refresh_data.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )