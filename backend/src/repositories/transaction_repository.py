from sqlalchemy import func
from sqlalchemy.orm import Session

from models.transaction import Transaction, TransactionType, TransactionStatus


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        type: TransactionType,
        amount,
        reference: str | None = None,
        status: TransactionStatus = TransactionStatus.COMPLETED,
    ):
        transaction = Transaction(
            user_id=user_id,
            type=type,
            amount=amount,
            reference=reference,
            status=status,
        )

        self.db.add(transaction)
        self.db.flush()

        return transaction

    def get_by_id(
        self,
        transaction_id: int,
    ):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.id == transaction_id
            )
            .first()
        )

    def get_by_user_id(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id
            )
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_all(
        self,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Transaction)
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_balance(
        self,
        user_id: int,
    ):
        total = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user_id,
                Transaction.status == TransactionStatus.COMPLETED,
            )
            .scalar()
        )

        return total or 0