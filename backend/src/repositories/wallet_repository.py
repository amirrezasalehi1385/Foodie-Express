from decimal import Decimal

from sqlalchemy.orm import Session

from models.wallet import Wallet


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        balance: Decimal = Decimal("0.00"),
    ):
        wallet = Wallet(
            user_id=user_id,
            balance=balance,
        )

        self.db.add(wallet)
        self.db.flush()

        return wallet

    def get_by_id(
        self,
        wallet_id: int,
    ):
        return (
            self.db.query(Wallet)
            .filter(
                Wallet.id == wallet_id
            )
            .first()
        )

    def get_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Wallet)
            .filter(
                Wallet.user_id == user_id
            )
            .first()
        )

    def get_by_user_id_for_update(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Wallet)
            .filter(
                Wallet.user_id == user_id
            )
            .with_for_update()
            .first()
        )

    def update(self, wallet: Wallet):
        self.db.add(wallet)
        self.db.flush()

        return wallet