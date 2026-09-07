from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from dto.payment import (
    PaymentResponse,
    PaymentConfirmRequest,
    PaymentInitiateResponse,
)
from services.payment_service import PaymentService


router = APIRouter(
    tags=["Payments"],
)


@router.post(
    "/orders/{order_id}/payment",
    response_model=PaymentInitiateResponse,
    status_code=status.HTTP_201_CREATED,
)
def initiate_payment(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment_service = PaymentService(db)

    try:
        payment = payment_service.initiate_payment(
            user_id=current_user.id,
            order_id=order_id,
        )

        db.commit()
        db.refresh(payment)

        return PaymentInitiateResponse(
            id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
            payment_token=payment.payment_token,
            checkout_url=f"/fake-checkout/{payment.payment_token}",
        )

    except Exception:
        db.rollback()
        raise


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment_service = PaymentService(db)

    return payment_service.get_payment(
        current_user=current_user,
        payment_id=payment_id,
    )


@router.get(
    "/fake-checkout/{token}",
    response_model=PaymentResponse,
)
def get_checkout_details(
    token: str,
    db: Session = Depends(get_db),
):
    payment_service = PaymentService(db)

    return payment_service.get_payment_by_token(
        payment_token=token,
    )


@router.post(
    "/fake-checkout/{token}/confirm",
    response_model=PaymentResponse,
)
def confirm_payment(
    token: str,
    data: PaymentConfirmRequest,
    db: Session = Depends(get_db),
):
    payment_service = PaymentService(db)

    try:
        payment = payment_service.confirm_payment(
            payment_token=token,
            card_number=data.card_number,
        )

        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
)
def get_all_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payment_service = PaymentService(db)

    return payment_service.get_all_payments(
        current_user=current_user,
        page=page,
        limit=limit,
    )