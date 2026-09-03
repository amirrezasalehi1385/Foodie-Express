from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    menu_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("menus.id"),
        primary_key=True,
    )

    food_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("foods.id"),
        primary_key=True,
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )