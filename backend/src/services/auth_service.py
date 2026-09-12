from datetime import datetime, timezone

import jwt
from sqlalchemy.orm import Session

from dto.user import UserCreate
from models.user import User
from models.refresh_token import RefreshToken
from services.user_service import UserService
from utils.security import (
    DUMMY_HASH,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
)

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def authenticate_user(
        self,
        phone: str,
        password: str,
    ) -> User | None:

        user = self.user_service.get_user_by_phone(phone)

        if not user:
            verify_password(password, DUMMY_HASH)
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def register(self, user_data: UserCreate) -> User:
        existing_user = self.user_service.get_user_by_phone(user_data.phone)

        if existing_user:
            raise ValueError("Phone number already registered")

        if user_data.email:
            existing_user = self.user_service.get_user_by_email(user_data.email)

            if existing_user:
                raise ValueError("Email already registered")

        password_hash = get_password_hash(user_data.password)

        return self.user_service.create_user(
            user_data=user_data,
            password_hash=password_hash,
        )

    def login(
        self,
        phone: str,
        password: str,
    ) -> tuple[str, str]:

        user = self.authenticate_user(phone, password)

        if user is None:
            raise ValueError("Incorrect phone number or password")

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        self.db.add(
            RefreshToken(
                token_hash=hash_token(refresh_token),
                user_id=user.id,
            )
        )
        self.db.commit()

        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> tuple[str, str]:
        try:
            payload = decode_refresh_token(refresh_token)
        except jwt.PyJWTError:
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid refresh token")

        token_hash = hash_token(refresh_token)

        token_in_db = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )

        if not token_in_db:
            raise ValueError("Refresh token not found")

        if token_in_db.revoked:
            # Reuse of an already-rotated token = theft signal.
            # Nuke every session on this account, attacker included.
            self.db.query(RefreshToken).filter(
                RefreshToken.user_id == token_in_db.user_id,
                RefreshToken.revoked == False,  # noqa: E712
            ).update({"revoked": True})
            self.db.commit()
            raise ValueError("Refresh token reuse detected — all sessions revoked, please log in again")

        if token_in_db.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        user = self.user_service.get_user_by_id(int(user_id))
        if not user:
            raise ValueError("User not found")

        token_in_db.revoked = True

        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        self.db.add(
            RefreshToken(
                token_hash=hash_token(new_refresh_token),
                user_id=user.id,
            )
        )
        self.db.commit()

        return new_access_token, new_refresh_token

    def logout(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)

        token_in_db = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )

        if not token_in_db:
            raise ValueError("Refresh token not found")

        token_in_db.revoked = True
        self.db.commit()