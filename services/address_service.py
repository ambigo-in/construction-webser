"""Address business logic."""
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from repositories import address_repository
from schemas.address_schemas import AddressCreate, AddressUpdate


def list_my_addresses(db: Session, user: User):
    return address_repository.list_addresses(db, user.id)


def create_my_address(db: Session, user: User, payload: AddressCreate):
    address = address_repository.create_address(db, {"user_id": user.id, **payload.model_dump()})
    db.commit()
    db.refresh(address)
    return address


def update_my_address(db: Session, user: User, address_id: UUID, payload: AddressUpdate):
    address = address_repository.get_address(db, address_id)
    if not address or address.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    address = address_repository.update_address(db, address, payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(address)
    return address


def delete_my_address(db: Session, user: User, address_id: UUID):
    address = address_repository.get_address(db, address_id)
    if not address or address.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    address_repository.delete_address(db, address)
    db.commit()

