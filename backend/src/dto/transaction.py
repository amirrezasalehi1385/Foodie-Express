from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from models.transaction import TransactionType, TransactionStatus


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: TransactionType
    amount: Decimal
    reference: str | None
    status: TransactionStatus
    created_at: datetime


class WalletBalanceResponse(BaseModel):
    balance: Decimal


class WalletTopupRequest(BaseModel):
    amount: Decimal