from sqlalchemy import func
from sqlalchemy.orm import Session

from models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: int,
        user_id: int,
        restaurant_id: int,
        rating: int,
        comment: str | None = None,
    ):
        review = Review(
            order_id=order_id,
            user_id=user_id,
            restaurant_id=restaurant_id,
            rating=rating,
            comment=comment,
        )

        self.db.add(review)
        self.db.flush()

        return review

    def get_by_id(
        self,
        review_id: int,
    ):
        return (
            self.db.query(Review)
            .filter(
                Review.id == review_id
            )
            .first()
        )

    def get_by_order_id(
        self,
        order_id: int,
    ):
        return (
            self.db.query(Review)
            .filter(
                Review.order_id == order_id
            )
            .first()
        )

    def get_by_restaurant_id(
        self,
        restaurant_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Review)
            .filter(
                Review.restaurant_id == restaurant_id
            )
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_user_id(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Review)
            .filter(
                Review.user_id == user_id
            )
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_average_rating(
        self,
        restaurant_id: int,
    ):
        result = (
            self.db.query(
                func.avg(Review.rating),
                func.count(Review.id),
            )
            .filter(Review.restaurant_id == restaurant_id)
            .first()
        )

        average, count = result

        return {
            "average_rating": round(float(average), 2) if average is not None else 0.0,
            "review_count": count,
        }

    def update(self, review: Review):
        self.db.add(review)
        self.db.flush()

        return review

    def delete(self, review: Review):
        self.db.delete(review)
        self.db.flush()