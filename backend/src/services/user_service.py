
from sqlalchemy.orm import Session

from dto.user import AdminUserUpdate, UserCreate, UserUpdate
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
    
    def update_user(self, user: User, user_data: UserUpdate) -> User:
        update_data = user_data.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing_user = self.user_repository.get_by_email(
                update_data["email"]
            )

            if existing_user and existing_user.id != user.id:
                raise ValueError("Email already registered")

        return self.user_repository.update(
            user,
            update_data,
        )
    def get_users(self) -> list[User] : 
        return self.user_repository.get_all()

    def admin_update_user(
        self,
        user: User,
        user_data: AdminUserUpdate,
    ) -> User:

        update_data = user_data.model_dump(exclude_unset=True)

        if "phone" in update_data:
            existing_user = self.user_repository.get_by_phone(
                update_data["phone"]
            )

            if existing_user and existing_user.id != user.id:
                raise ValueError("Phone number already registered")

        if "email" in update_data:
            existing_user = self.user_repository.get_by_email(
                update_data["email"]
            )

            if existing_user and existing_user.id != user.id:
                raise ValueError("Email already registered")

        return self.user_repository.update(
            user,
            update_data,
        )