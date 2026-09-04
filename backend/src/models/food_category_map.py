from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class FoodCategoryMap(Base):
    __tablename__ = "food_category_map"

    food_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("foods.id"),
        primary_key=True,
    )

    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("food_categories.id"),
        primary_key=True,
    )