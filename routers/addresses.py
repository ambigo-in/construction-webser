"""Buyer address routes."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models import User
from schemas.address_schemas import AddressCreate, AddressResponse, AddressUpdate
from services import address_service

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", response_model=list[AddressResponse])
def list_addresses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return address_service.list_my_addresses(db, user)


@router.post("", response_model=AddressResponse)
def create_address(payload: AddressCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return address_service.create_my_address(db, user, payload)


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(address_id: UUID, payload: AddressUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return address_service.update_my_address(db, user, address_id, payload)


@router.delete("/{address_id}", status_code=204)
def delete_address(address_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    address_service.delete_my_address(db, user, address_id)

