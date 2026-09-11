from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from models.order import OrderStatus

if TYPE_CHECKING:
    from models.order import Order
    from models.user import User


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id"),
        nullable=False,
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(
            OrderStatus,
            native_enum=False,
            length=40,
        ),
        nullable=False,
    )

    changed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    order: Mapped["Order"] = relationship(
        "Order",
    )

    changed_by_user: Mapped["User | None"] = relationship(
        "User",
    )