from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.wallet import Wallet
from models.transaction import TransactionType, TransactionStatus

from repositories.wallet_repository import WalletRepository
from repositories.transaction_repository import TransactionRepository


class WalletService:
    def __init__(self, db: Session):
        self.wallet_repository = WalletRepository(db)
        self.transaction_repository = TransactionRepository(db)

    def get_or_create_wallet(
        self,
        user_id: int,
    ):
        wallet = self.wallet_repository.get_by_user_id(
            user_id=user_id,
        )

        if wallet is None:
            wallet = self.wallet_repository.create(
                user_id=user_id,
            )

        return wallet

    def get_balance(
        self,
        user_id: int,
    ):
        wallet = self.get_or_create_wallet(user_id=user_id)

        return wallet.balance

    def credit(
        self,
        user_id: int,
        amount: Decimal,
        type: TransactionType,
        reference: str | None = None,
    ):
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credit amount must be positive",
            )

        wallet = self.wallet_repository.get_by_user_id_for_update(
            user_id=user_id,
        )

        if wallet is None:
            wallet = self.wallet_repository.create(
                user_id=user_id,
            )

        wallet.balance += amount
        self.wallet_repository.update(wallet)

        self.transaction_repository.create(
            user_id=user_id,
            type=type,
            amount=amount,
            reference=reference,
            status=TransactionStatus.COMPLETED,
        )

        return wallet

    def debit(
        self,
        user_id: int,
        amount: Decimal,
        type: TransactionType,
        reference: str | None = None,
    ):
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debit amount must be positive",
            )

        wallet = self.wallet_repository.get_by_user_id_for_update(
            user_id=user_id,
        )

        if wallet is None or wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient wallet balance",
            )

        wallet.balance -= amount
        self.wallet_repository.update(wallet)

        self.transaction_repository.create(
            user_id=user_id,
            type=type,
            amount=-amount,
            reference=reference,
            status=TransactionStatus.COMPLETED,
        )

        return wallet

    def get_transactions(
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