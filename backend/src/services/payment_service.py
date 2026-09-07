import random
import string
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.order import Order, OrderStatus
from models.payment import Payment, PaymentStatus, PaymentMethod
from models.user import User, UserRole

from repositories.payment_repository import PaymentRepository
from repositories.order_repository import OrderRepository


class PaymentService:
    def __init__(self, db: Session):
        self.payment_repository = PaymentRepository(db)
        self.order_repository = OrderRepository(db)

    def initiate_payment(
        self,
        user_id: int,
        order_id: int,
    ):
        order = self.order_repository.get_by_id(order_id=order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this order",
            )

        if order.status != OrderStatus.PENDING_PAYMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not awaiting payment",
            )

        existing = self.payment_repository.get_by_order_id(
            order_id=order.id,
        )

        if existing and existing.status == PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has already been paid",
            )

        if existing and existing.status == PaymentStatus.PENDING:
            return existing

        payment = self.payment_repository.create(
            order_id=order.id,
            amount=order.total_amount,
            method=PaymentMethod.CARD,
        )

        return payment

    def get_payment_by_token(
        self,
        payment_token: str,
    ):
        payment = self.payment_repository.get_by_token(
            payment_token=payment_token,
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        return payment

    def confirm_payment(
        self,
        payment_token: str,
        card_number: str,
    ):
        payment = self.payment_repository.get_by_token(
            payment_token=payment_token,
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has already been processed",
            )

        order = self.order_repository.get_by_id(
            order_id=payment.order_id,
        )

        payment.card_last_four = card_number[-4:]

        # simulate a ~10% decline rate for realism
        is_successful = random.random() > 0.10

        if is_successful:
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.now(timezone.utc)
            payment.receipt_number = self._generate_receipt_number()

            order.status = OrderStatus.PAID
            self.order_repository.update(order)
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = random.choice(
                [
                    "Insufficient funds",
                    "Card declined by issuer",
                    "Transaction timed out",
                ]
            )

            order.status = OrderStatus.PAYMENT_FAILED
            self.order_repository.update(order)

        self.payment_repository.update(payment)

        return payment

    def get_payment(
        self,
        current_user: User,
        payment_id: int,
    ):
        payment = self.payment_repository.get_by_id(
            payment_id=payment_id,
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        order = self.order_repository.get_by_id(
            order_id=payment.order_id,
        )

        if (
            current_user.role != UserRole.ADMIN
            and order.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this payment",
            )

        return payment

    def get_all_payments(
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

        return self.payment_repository.get_all(
            offset=offset,
            limit=limit,
        )
        
        
    def _generate_receipt_number(self) -> str:
        date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
        random_part = "".join(
            random.choices(string.digits, k=6)
        )

        return f"RCPT-{date_part}-{random_part}"