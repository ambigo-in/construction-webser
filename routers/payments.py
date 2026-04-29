"""Payment, delivery, and review routes."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models import User
from schemas.transaction_schemas import DeliveryResponse, DeliveryUpdate, ReviewCreate, ReviewResponse
from services import payment_service, review_service

router = APIRouter(tags=["payments-delivery-reviews"])


@router.get("/deliveries/order/{order_id}", response_model=DeliveryResponse)
def get_delivery(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return payment_service.get_delivery_by_order(db, user, order_id)


@router.patch("/deliveries/order/{order_id}", response_model=DeliveryResponse)
def update_delivery(
    order_id: UUID,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return payment_service.update_delivery_status(db, user, order_id, payload)


@router.post("/reviews", response_model=ReviewResponse)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return review_service.create_review(db, user, payload)
