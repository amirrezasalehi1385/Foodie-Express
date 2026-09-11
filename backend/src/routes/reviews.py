from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from dto.review import (
    ReviewCreateRequest,
    ReviewUpdateRequest,
    ReviewResponse,
    RestaurantRatingSummaryResponse,
)
from services.review_service import ReviewService


router = APIRouter(
    tags=["Reviews"],
)


@router.post(
    "/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    data: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    try:
        review = review_service.create_review(
            user_id=current_user.id,
            order_id=data.order_id,
            rating=data.rating,
            comment=data.comment,
        )

        db.commit()
        db.refresh(review)

        return review

    except Exception:
        db.rollback()
        raise


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    return review_service.get_review(
        review_id=review_id,
    )


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    data: ReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    try:
        review = review_service.update_review(
            current_user=current_user,
            review_id=review_id,
            rating=data.rating,
            comment=data.comment,
        )

        db.commit()
        db.refresh(review)

        return review

    except Exception:
        db.rollback()
        raise


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    try:
        review_service.delete_review(
            current_user=current_user,
            review_id=review_id,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


@router.get(
    "/restaurants/{restaurant_id}/reviews",
    response_model=list[ReviewResponse],
)
def get_restaurant_reviews(
    restaurant_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    return review_service.get_restaurant_reviews(
        restaurant_id=restaurant_id,
        page=page,
        limit=limit,
    )


@router.get(
    "/restaurants/{restaurant_id}/reviews/summary",
    response_model=RestaurantRatingSummaryResponse,
)
def get_restaurant_rating_summary(
    restaurant_id: int,
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    summary = review_service.get_restaurant_rating_summary(
        restaurant_id=restaurant_id,
    )

    return RestaurantRatingSummaryResponse(**summary)


@router.get(
    "/users/me/reviews",
    response_model=list[ReviewResponse],
)
def get_my_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review_service = ReviewService(db)

    return review_service.get_my_reviews(
        user_id=current_user.id,
        page=page,
        limit=limit,
    )