from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.review import Review
from models.order import OrderStatus
from models.user import User, UserRole

from repositories.review_repository import ReviewRepository
from repositories.order_repository import OrderRepository


class ReviewService:
    def __init__(self, db: Session):
        self.review_repository = ReviewRepository(db)
        self.order_repository = OrderRepository(db)

    def create_review(
        self,
        user_id: int,
        order_id: int,
        rating: int,
        comment: str | None = None,
    ) -> Review:
        if not (1 <= rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5",
            )

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

        if order.status != OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only review an order after it has been delivered",
            )

        existing = self.review_repository.get_by_order_id(order_id=order_id)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this order",
            )

        review = self.review_repository.create(
            order_id=order.id,
            user_id=user_id,
            restaurant_id=order.restaurant_id,
            rating=rating,
            comment=comment,
        )

        return review

    def get_review(
        self,
        review_id: int,
    ) -> Review:
        review = self.review_repository.get_by_id(review_id=review_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        return review

    def get_restaurant_reviews(
        self,
        restaurant_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        offset = (page - 1) * limit

        return self.review_repository.get_by_restaurant_id(
            restaurant_id=restaurant_id,
            offset=offset,
            limit=limit,
        )

    def get_my_reviews(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 10,
    ):
        offset = (page - 1) * limit

        return self.review_repository.get_by_user_id(
            user_id=user_id,
            offset=offset,
            limit=limit,
        )

    def get_restaurant_rating_summary(
        self,
        restaurant_id: int,
    ):
        return self.review_repository.get_average_rating(
            restaurant_id=restaurant_id,
        )

    def update_review(
        self,
        current_user: User,
        review_id: int,
        rating: int | None = None,
        comment: str | None = None,
    ) -> Review:
        review = self.review_repository.get_by_id(review_id=review_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        if review.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this review",
            )

        if rating is not None:
            if not (1 <= rating <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5",
                )
            review.rating = rating

        if comment is not None:
            review.comment = comment

        self.review_repository.update(review)

        return review

    def delete_review(
        self,
        current_user: User,
        review_id: int,
    ):
        review = self.review_repository.get_by_id(review_id=review_id)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        if current_user.role != UserRole.ADMIN and review.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this review",
            )

        self.review_repository.delete(review)