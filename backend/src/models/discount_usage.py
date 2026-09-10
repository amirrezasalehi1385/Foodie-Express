from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base

if TYPE_CHECKING:
    from models.discount import Discount
    from models.user import User
    from models.order import Order


class DiscountUsage(Base):
    __tablename__ = "discount_usages"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    discount_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("discounts.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id"),
        nullable=False,
        unique=True,  # one discount usage per order
    )

    amount_saved: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    discount: Mapped["Discount"] = relationship(
        "Discount",
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    order: Mapped["Order"] = relationship(
        "Order",
    )