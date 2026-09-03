from sqlalchemy.orm import Session

from models.restaurant_category_map import RestaurantCategoryMap


class RestaurantCategoryMapRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        restaurant_id: int,
        category_id: int,
    ):
        mapping = RestaurantCategoryMap(
            restaurant_id=restaurant_id,
            category_id=category_id,
        )

        self.db.add(mapping)
        self.db.flush()

        return mapping

    def get_by_restaurant_id(
        self,
        restaurant_id: int,
    ):
        return (
            self.db.query(RestaurantCategoryMap)
            .filter(
                RestaurantCategoryMap.restaurant_id == restaurant_id
            )
            .all()
        )

    def get_by_restaurant_and_category(
        self,
        restaurant_id: int,
        category_id: int,
    ):
        return (
            self.db.query(RestaurantCategoryMap)
            .filter(
                RestaurantCategoryMap.restaurant_id == restaurant_id,
                RestaurantCategoryMap.category_id == category_id,
            )
            .first()
        )

    def delete(self, mapping: RestaurantCategoryMap):
        self.db.delete(mapping)
        self.db.flush()