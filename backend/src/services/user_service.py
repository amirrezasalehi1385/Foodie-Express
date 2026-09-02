from sqlalchemy.orm import Session

from dto.user import UserCreate
from models.user import User, UserRole, UserStatus
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def get_user_by_phone(self, phone: str) -> User | None:
        return self.user_repository.get_by_phone(phone)

    def get_user_by_email(self, email: str) -> User | None:
        return self.user_repository.get_by_email(email)

    def create_user(self, user_data: UserCreate, password_hash: str) -> User:
        user = User(
            full_name=user_data.full_name,
            phone=user_data.phone,
            email=user_data.email,
            password_hash=password_hash,
            role=UserRole.CUSTOMER,
            status=UserStatus.ACTIVE,
        )

        return self.user_repository.create(user)