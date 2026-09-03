from sqlalchemy.orm import Session

from dto.menu import MenuUpdate
from models.menu import Menu
from repositories.base_repository import BaseRepository


class MenuRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Menu)

    def get_by_restaurant_id(
        self,
        restaurant_id: int,
    ):
        return (
            self.db.query(Menu)
            .filter(Menu.restaurant_id == restaurant_id)
            .order_by(Menu.display_order.asc(), Menu.id.asc())
            .all()
        )

    def update(
        self,
        menu_id: int,
        menu_data: MenuUpdate,
    ):
        menu = (
            self.db.query(Menu)
            .filter(Menu.id == menu_id)
            .first()
        )

        if menu is None:
            return None

        update_data = menu_data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(menu, field, value)

        self.db.flush()
        self.db.refresh(menu)

        return menu