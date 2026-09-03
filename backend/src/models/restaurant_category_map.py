from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class RestaurantCategoryMap(Base):
    __tablename__ = "restaurant_category_map"

    restaurant_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("restaurants.id"),
        primary_key=True,
    )

    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("restaurant_categories.id"),
        primary_key=True,
    )