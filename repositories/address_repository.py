"""Address database operations."""
from uuid import UUID

from sqlalchemy.orm import Session

from models import Address


def list_addresses(db: Session, user_id: UUID):
    return db.query(Address).filter(Address.user_id == user_id).order_by(Address.created_at.desc()).all()


def get_address(db: Session, address_id: UUID):
    return db.query(Address).filter(Address.id == address_id).first()


def create_address(db: Session, data: dict):
    address = Address(**data)
    db.add(address)
    db.flush()
    return address


def update_address(db: Session, address: Address, data: dict):
    for key, value in data.items():
        setattr(address, key, value)
    db.flush()
    return address


def delete_address(db: Session, address: Address):
    db.delete(address)
    db.flush()

