"""Seller profile database operations."""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import Order, SellerProfile, SellerProduct


def get_seller_by_user_id(db: Session, user_id: UUID) -> Optional[SellerProfile]:
    return db.query(SellerProfile).filter(SellerProfile.user_id == user_id).first()


def get_seller(db: Session, seller_id: UUID) -> Optional[SellerProfile]:
    return db.query(SellerProfile).filter(SellerProfile.id == seller_id).first()


def create_seller_profile(db: Session, data: dict) -> SellerProfile:
    seller = SellerProfile(**data)
    db.add(seller)
    db.flush()
    return seller


def update_seller_profile(db: Session, seller: SellerProfile, data: dict) -> SellerProfile:
    for key, value in data.items():
        setattr(seller, key, value)
    db.flush()
    return seller


def list_sellers(db: Session, *, approval_status: Optional[str] = None):
    query = db.query(SellerProfile).order_by(SellerProfile.created_at.desc())
    if approval_status:
        query = query.filter(SellerProfile.approval_status == approval_status)
    return query.all()


def seller_dashboard_counts(db: Session, seller_id: UUID):
    active_products = (
        db.query(SellerProduct)
        .filter(SellerProduct.seller_id == seller_id, SellerProduct.status == "active")
        .count()
    )
    pending_orders = (
        db.query(Order)
        .filter(Order.seller_id == seller_id, Order.order_status.in_(["placed", "confirmed", "dispatched"]))
        .count()
    )
    completed_orders = (
        db.query(Order)
        .filter(Order.seller_id == seller_id, Order.order_status == "delivered")
        .count()
    )
    delivered_orders = db.query(Order).filter(Order.seller_id == seller_id, Order.order_status == "delivered").all()
    revenue = sum((order.total_amount or 0) for order in delivered_orders)
    return active_products, pending_orders, completed_orders, revenue

