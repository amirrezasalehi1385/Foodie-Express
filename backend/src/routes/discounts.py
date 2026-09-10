from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from dto.discount import (
    DiscountCreateRequest,
    DiscountResponse,
    DiscountPreviewRequest,
    DiscountPreviewResponse,
)
from services.discount_service import DiscountService


router = APIRouter(
    prefix="/discounts",
    tags=["Discounts"],
)


@router.post(
    "",
    response_model=DiscountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discount(
    data: DiscountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    try:
        discount = discount_service.create_discount(
            current_user=current_user,
            code=data.code,
            type=data.type,
            value=data.value,
            restaurant_id=data.restaurant_id,
            min_order_amount=data.min_order_amount,
            max_discount_amount=data.max_discount_amount,
            usage_limit=data.usage_limit,
            usage_limit_per_user=data.usage_limit_per_user,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
        )

        db.commit()
        db.refresh(discount)

        return discount

    except Exception:
        db.rollback()
        raise


@router.get(
    "",
    response_model=list[DiscountResponse],
)
def get_all_discounts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    return discount_service.get_all_discounts(
        current_user=current_user,
        page=page,
        limit=limit,
    )


@router.get(
    "/{discount_id}",
    response_model=DiscountResponse,
)
def get_discount(
    discount_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    return discount_service.get_discount(
        current_user=current_user,
        discount_id=discount_id,
    )


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[DiscountResponse],
)
def get_restaurant_discounts(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    return discount_service.get_restaurant_discounts(
        current_user=current_user,
        restaurant_id=restaurant_id,
        page=page,
        limit=limit,
    )


@router.post(
    "/{discount_id}/deactivate",
    response_model=DiscountResponse,
)
def deactivate_discount(
    discount_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    try:
        discount = discount_service.deactivate_discount(
            current_user=current_user,
            discount_id=discount_id,
        )

        db.commit()
        db.refresh(discount)

        return discount

    except Exception:
        db.rollback()
        raise


@router.post(
    "/preview",
    response_model=DiscountPreviewResponse,
)
def preview_discount(
    data: DiscountPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    discount_service = DiscountService(db)

    _, discount_amount = discount_service.validate_and_calculate(
        code=data.code,
        user_id=current_user.id,
        restaurant_id=data.restaurant_id,
        subtotal=data.subtotal,
    )

    return DiscountPreviewResponse(discount_amount=discount_amount)