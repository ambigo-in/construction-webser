"""Payment and manual delivery business logic."""
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from repositories import audit_repository, order_repository, seller_repository
from schemas.marketplace_schemas import PaymentStatusUpdate
from schemas.transaction_schemas import DeliveryUpdate
from utils.constants import DELIVERY_STATUSES, PAYMENT_STATUSES


def list_payments(db: Session):
    return order_repository.list_payments(db)


def get_payment(db: Session, payment_id: UUID):
    payment = order_repository.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment


def update_payment_status(db: Session, admin: User, payment_id: UUID, payload: PaymentStatusUpdate):
    if payload.payment_status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment_status")
    payment = get_payment(db, payment_id)
    data = payload.model_dump(exclude_unset=True)
    if payload.payment_status == "completed":
        data["paid_at"] = datetime.utcnow()
        payment.order.payment_status = "completed"
    else:
        payment.order.payment_status = payload.payment_status
    payment = order_repository.update_payment(db, payment, data)
    audit_repository.create_audit_log(
        db,
        user_id=admin.id,
        action="payment_status_updated",
        entity_type="payment",
        entity_id=payment.id,
        meta={"payment_status": payload.payment_status},
    )
    db.commit()
    db.refresh(payment)
    return payment


def _role_names(user: User) -> set[str]:
    return {role.role_name.lower() for role in (user.roles or [])}


def _can_view_order_delivery(db: Session, user: User, order) -> bool:
    if "admin" in _role_names(user):
        return True
    if order.buyer_id == user.id:
        return True
    seller = seller_repository.get_seller_by_user_id(db, user.id)
    return bool(seller and order.seller_id == seller.id)


def _can_update_order_delivery(db: Session, user: User, order) -> bool:
    if "admin" in _role_names(user):
        return True
    seller = seller_repository.get_seller_by_user_id(db, user.id)
    return bool(seller and order.seller_id == seller.id)


def get_delivery_by_order(db: Session, user: User, order_id: UUID):
    order = order_repository.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if not _can_view_order_delivery(db, user, order):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this delivery")
    delivery = order_repository.get_delivery_by_order(db, order_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return delivery


def update_delivery_status(db: Session, user: User, order_id: UUID, payload: DeliveryUpdate):
    order = order_repository.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if not _can_update_order_delivery(db, user, order):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this delivery")
    delivery = order_repository.get_delivery_by_order(db, order_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    data = payload.model_dump(exclude_unset=True)
    status_value = data.get("delivery_status")
    if status_value and status_value not in DELIVERY_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid delivery_status")
    if status_value == "dispatched":
        data["dispatch_time"] = datetime.utcnow()
    if status_value == "delivered":
        data["delivered_time"] = datetime.utcnow()
    delivery = order_repository.update_delivery(db, delivery, data)
    audit_repository.create_audit_log(
        db,
        user_id=user.id,
        action="delivery_status_updated",
        entity_type="delivery",
        entity_id=delivery.id,
        meta=data,
    )
    db.commit()
    db.refresh(delivery)
    return delivery
