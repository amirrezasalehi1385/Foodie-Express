from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from models.transaction import TransactionType
from dto.transaction import TransactionResponse, WalletBalanceResponse, WalletTopupRequest
from services.transaction_service import TransactionService
from services.wallet_service import WalletService


router = APIRouter(
    tags=["Wallet & Transactions"],
)


@router.get(
    "/wallet/balance",
    response_model=WalletBalanceResponse,
)
def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet_service = WalletService(db)

    balance = wallet_service.get_balance(user_id=current_user.id)

    return WalletBalanceResponse(balance=balance)


@router.post(
    "/wallet/topup",
    response_model=WalletBalanceResponse,
)
def topup_wallet(
    data: WalletTopupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet_service = WalletService(db)

    try:
        wallet = wallet_service.credit(
            user_id=current_user.id,
            amount=data.amount,
            type=TransactionType.TOPUP,
            reference="manual-topup",
        )

        db.commit()
        db.refresh(wallet)

        return WalletBalanceResponse(balance=wallet.balance)

    except Exception:
        db.rollback()
        raise


@router.get(
    "/users/me/transactions",
    response_model=list[TransactionResponse],
)
def get_my_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction_service = TransactionService(db)

    return transaction_service.get_my_transactions(
        user_id=current_user.id,
        page=page,
        limit=limit,
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction_service = TransactionService(db)

    return transaction_service.get_transaction(
        current_user=current_user,
        transaction_id=transaction_id,
    )


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
def get_all_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction_service = TransactionService(db)

    return transaction_service.get_all_transactions(
        current_user=current_user,
        page=page,
        limit=limit,
    )