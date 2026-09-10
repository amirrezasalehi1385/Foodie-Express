from decimal import Decimal

from sqlalchemy.orm import Session

from models.discount_usage import DiscountUsage


class DiscountUsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        discount_id: int,
        user_id: int,
        order_id: int,
        amount_saved: Decimal,
    ):
        usage = DiscountUsage(
            discount_id=discount_id,
            user_id=user_id,
            order_id=order_id,
            amount_saved=amount_saved,
        )

        self.db.add(usage)
        self.db.flush()

        return usage

    def get_total_usage_count(
        self,
        discount_id: int,
    ) -> int:
        return (
            self.db.query(DiscountUsage)
            .filter(
                DiscountUsage.discount_id == discount_id
            )
            .count()
        )

    def get_user_usage_count(
        self,
        discount_id: int,
        user_id: int,
    ) -> int:
        return (
            self.db.query(DiscountUsage)
            .filter(
                DiscountUsage.discount_id == discount_id,
                DiscountUsage.user_id == user_id,
            )
            .count()
        )

    def get_by_order_id(
        self,
        order_id: int,
    ):
        return (
            self.db.query(DiscountUsage)
            .filter(
                DiscountUsage.order_id == order_id
            )
            .first()
        )