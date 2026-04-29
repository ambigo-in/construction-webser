"""Buyer cart routes."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models import User
from schemas.cart_schemas import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse, CartSummary
from services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_service.get_my_cart(db, user)


@router.get("/summary", response_model=CartSummary)
def get_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_service.get_cart_summary(db, user)


@router.post("/items", response_model=CartItemResponse)
def add_item(payload: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_service.add_cart_item(db, user, payload)


@router.patch("/items/{item_id}", response_model=CartItemResponse)
def update_item(item_id: UUID, payload: CartItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_service.update_cart_item(db, user, item_id, payload)


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart_service.delete_cart_item(db, user, item_id)

