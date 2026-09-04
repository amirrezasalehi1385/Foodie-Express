from sqlalchemy.orm import Session

from dto.user import UserCreate
from models.user import User
from services.user_service import UserService
from utils.security import (
    DUMMY_HASH,
    create_access_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    def __init__(self, db: Session):
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

        existing_user = self.user_service.get_user_by_phone(
            user_data.phone
        )

        if existing_user:
            raise ValueError("Phone number already registered")

        if user_data.email:
            existing_user = self.user_service.get_user_by_email(
                user_data.email
            )

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
    ) -> str:

        user = self.authenticate_user(phone, password)

        if user is None:
            raise ValueError("Incorrect phone number or password")

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        return access_token