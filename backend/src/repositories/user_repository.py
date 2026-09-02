from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_phone(self, phone: str) -> User | None:
        stmt = select(User).where(User.phone == phone)

        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)

        return self.db.scalar(stmt)
    