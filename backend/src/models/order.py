from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base
from enum import Enum
from sqlalchemy import Enum as SQLEnum

if TYPE_CHECKING:
    from models.user import User
    from models.restaurant import Restaurant
    from models.address import Address
    # from models.discount import Discount
    from models.order_items import OrderItem
    # from models.order_status_history import OrderStatusHistory

class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY = "READY"
    ASSIGNED = "ASSIGNED"        # driver claimed it, hasn't picked up yet
    DELIVERING = "DELIVERING"    # driver has physically picked up food
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    PAYMENT_FAILED = "PAYMENT_FAILED"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )

    restaurant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("restaurants.id"),
        nullable=False,
    )

    delivery_address_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("addresses.id"),
        nullable=False,
    )

    # discount_id: Mapped[int | None] = mapped_column(
    #     BigInteger,
    #     ForeignKey("discounts.id"),
    #     nullable=True,
    # )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(
            OrderStatus,
            native_enum=False,
            length=40
        ),
        nullable=False,
        default=OrderStatus.PENDING_PAYMENT
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        "User",
    )

    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant",
    )

    delivery_address: Mapped["Address"] = relationship(
        "Address",
    )

    # discount: Mapped["Discount | None"] = relationship(
    #     "Discount",
    # )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    # status_history: Mapped[list["OrderStatusHistory"]] = relationship(
    #     "OrderStatusHistory",
    #     back_populates="order",
    #     cascade="all, delete-orphan",
    # )


