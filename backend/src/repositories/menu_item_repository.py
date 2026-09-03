from sqlalchemy.orm import Session

from models.menu_item import MenuItem


class MenuItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        menu_id: int,
        food_id: int,
        display_order: int = 0,
    ):
        menu_item = MenuItem(
            menu_id=menu_id,
            food_id=food_id,
            display_order=display_order,
        )

        self.db.add(menu_item)
        self.db.flush()

        return menu_item

    def get_by_menu_and_food(
        self,
        menu_id: int,
        food_id: int,
    ):
        return (
            self.db.query(MenuItem)
            .filter(
                MenuItem.menu_id == menu_id,
                MenuItem.food_id == food_id,
            )
            .first()
        )

    def get_by_menu_id(
        self,
        menu_id: int,
    ):
        return (
            self.db.query(MenuItem)
            .filter(MenuItem.menu_id == menu_id)
            .order_by(
                MenuItem.display_order.asc(),
                MenuItem.food_id.asc(),
            )
            .all()
        )

    def update_display_order(
        self,
        menu_id: int,
        food_id: int,
        display_order: int,
    ):
        menu_item = self.get_by_menu_and_food(
            menu_id=menu_id,
            food_id=food_id,
        )

        if menu_item is None:
            return None

        menu_item.display_order = display_order

        self.db.flush()
        self.db.refresh(menu_item)

        return menu_item

    def delete(
        self,
        menu_item: MenuItem,
    ):
        self.db.delete(menu_item)
        self.db.flush()