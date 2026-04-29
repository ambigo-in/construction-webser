"""Order database operations."""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import Delivery, Order, OrderItem, Payment, SellerPayout


def create_order(db: Session, data: dict, items: list[dict]) -> Order:
    order = Order(**data)
    db.add(order)
    db.flush()
    for item_data in items:
        db.add(OrderItem(order_id=order.id, **item_data))
    db.flush()
    return order


def get_order(db: Session, order_id: UUID) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()


def list_buyer_orders(db: Session, buyer_id: UUID):
    return db.query(Order).filter(Order.buyer_id == buyer_id).order_by(Order.created_at.desc()).all()


def list_seller_orders(db: Session, seller_id: UUID):
    return db.query(Order).filter(Order.seller_id == seller_id).order_by(Order.created_at.desc()).all()


def list_orders(db: Session, *, order_status: Optional[str] = None):
    query = db.query(Order).order_by(Order.created_at.desc())
    if order_status:
        query = query.filter(Order.order_status == order_status)
    return query.all()


def update_order_status(db: Session, order: Order, *, status: str, notes: Optional[str] = None):
    order.order_status = status
    if notes is not None:
        order.notes = notes
    db.flush()
    return order


def create_payment(db: Session, data: dict) -> Payment:
    payment = Payment(**data)
    db.add(payment)
    db.flush()
    return payment


def get_payment_by_order(db: Session, order_id: UUID):
    return db.query(Payment).filter(Payment.order_id == order_id).first()


def get_payment(db: Session, payment_id: UUID):
    return db.query(Payment).filter(Payment.id == payment_id).first()


def list_payments(db: Session):
    return db.query(Payment).order_by(Payment.created_at.desc()).all()


def update_payment(db: Session, payment: Payment, data: dict):
    for key, value in data.items():
        setattr(payment, key, value)
    db.flush()
    return payment


def create_delivery(db: Session, data: dict) -> Delivery:
    delivery = Delivery(**data)
    db.add(delivery)
    db.flush()
    return delivery


def get_delivery_by_order(db: Session, order_id: UUID):
    return db.query(Delivery).filter(Delivery.order_id == order_id).first()


def update_delivery(db: Session, delivery: Delivery, data: dict):
    for key, value in data.items():
        setattr(delivery, key, value)
    db.flush()
    return delivery


def create_payout(db: Session, data: dict) -> SellerPayout:
    payout = SellerPayout(**data)
    db.add(payout)
    db.flush()
    return payout

