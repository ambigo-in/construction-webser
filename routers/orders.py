"""Buyer order routes."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models import User
from schemas.marketplace_schemas import CheckoutCreate
from schemas.order_schemas import OrderResponse
from services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse)
def place_order(payload: CheckoutCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return order_service.place_order(db, user, payload)


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return order_service.list_my_orders(db, user)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return order_service.get_my_order(db, user, order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return order_service.cancel_my_order(db, user, order_id)

