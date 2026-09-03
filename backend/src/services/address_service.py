from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from dto.address import AddressCreate, AddressUpdate
from models.address import Address
from repositories.address_repository import AddressRepository


class AddressService:
    def __init__(self, db: Session):
        self.address_repository = AddressRepository(db)

    def create_address(
        self,
        address_data: AddressCreate,
        user_id: int,
    ):
        address = Address(
            user_id=user_id,
            title=address_data.title,
            recipient_name=address_data.recipient_name,
            phone=address_data.phone,
            province=address_data.province,
            city=address_data.city,
            address=address_data.address,
            postal_code=address_data.postal_code,
            latitude=address_data.latitude,
            longitude=address_data.longitude,
            is_default=address_data.is_default,
        )

        return self.address_repository.create(address)

    def get_user_addresses(
        self,
        user_id: int,
    ):
        return self.address_repository.get_by_user_id(user_id)

    def get_address_by_id(
        self,
        address_id: int,
        user_id: int,
    ):
        address = self.address_repository.get_by_id(address_id)

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )

        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this address",
            )

        return address

    def update_address(
        self,
        address_id: int,
        address_data: AddressUpdate,
        user_id: int,
    ):
        address = self.address_repository.get_by_id(address_id)

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )

        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this address",
            )

        return self.address_repository.update(
            address_id,
            address_data,
        )

    def delete_address(
        self,
        address_id: int,
        user_id: int,
    ):
        address = self.address_repository.get_by_id(address_id)

        if address is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )

        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this address",
            )

        self.address_repository.delete(address)