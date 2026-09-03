from sqlalchemy.orm import Session

from dto.address import AddressUpdate
from models.address import Address
from repositories.base_repository import BaseRepository


class AddressRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Address)

    def get_by_user_id(self, user_id: int):
        return (
            self.db.query(Address)
            .filter(Address.user_id == user_id)
            .all()
        )

    def update(
        self,
        address_id: int,
        address_data: AddressUpdate,
    ):
        address = (
            self.db.query(Address)
            .filter(Address.id == address_id)
            .first()
        )

        if address is None:
            return None

        update_data = address_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(address, field, value)

        self.db.flush()
        self.db.refresh(address)

        return address