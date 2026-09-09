from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.user import User, UserRole

from repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self, db: Session):
        self.transaction_repository = TransactionRepository(db)

    def get_my_transactions(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        offset = (page - 1) * limit

        return self.transaction_repository.get_by_user_id(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )

    def get_transaction(
        self,
        current_user: User,
        transaction_id: int,
    ):
        transaction = self.transaction_repository.get_by_id(
            transaction_id=transaction_id,
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        if (
            current_user.role != UserRole.ADMIN
            and transaction.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this transaction",
            )

        return transaction

    def get_all_transactions(
        self,
        current_user: User,
        page: int = 1,
        limit: int = 10,
    ):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource",
            )

        offset = (page - 1) * limit

        return self.transaction_repository.get_all(
            offset=offset,
            limit=limit,
        )