from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.discount import Discount, DiscountType


class DiscountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        code: str,
        type: DiscountType,
        value,
        restaurant_id: int | None = None,
        min_order_amount=None,
        max_discount_amount=None,
        usage_limit: int | None = None,
        usage_limit_per_user: int | None = 1,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
    ):
        discount = Discount(
            code=code,
            type=type,
            value=value,
            restaurant_id=restaurant_id,
            min_order_amount=min_order_amount,
            max_discount_amount=max_discount_amount,
            usage_limit=usage_limit,
            usage_limit_per_user=usage_limit_per_user,
            valid_from=valid_from,
            valid_until=valid_until,
        )

        self.db.add(discount)
        self.db.flush()

        return discount

    def get_by_id(
        self,
        discount_id: int,
    ):
        return (
            self.db.query(Discount)
            .filter(
                Discount.id == discount_id
            )
            .first()
        )

    def get_by_code(
        self,
        code: str,
    ):
        return (
            self.db.query(Discount)
            .filter(
                Discount.code == code
            )
            .first()
        )

    def get_by_code_for_update(
        self,
        code: str,
    ):
        return (
            self.db.query(Discount)
            .filter(
                Discount.code == code
            )
            .with_for_update()
            .first()
        )

    def get_all(
        self,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Discount)
            .order_by(Discount.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_restaurant_id(
        self,
        restaurant_id: int,
        offset: int = 0,
        limit: int = 10,
    ):
        return (
            self.db.query(Discount)
            .filter(
                Discount.restaurant_id == restaurant_id
            )
            .order_by(Discount.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update(self, discount: Discount):
        self.db.add(discount)
        self.db.flush()

        return discount