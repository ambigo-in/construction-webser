"""Admin business logic."""
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Order, SellerProfile, User
from repositories import audit_repository, user_repository
from schemas.marketplace_schemas import DashboardSummaryResponse
from schemas.user_schemas import UserUpdate


def list_users(db: Session):
    return user_repository.list_users(db)


def update_user_status(db: Session, admin: User, user_id: UUID, payload: UserUpdate):
    user = user_repository.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    user = user_repository.update_user(db, user, data)
    audit_repository.create_audit_log(
        db,
        user_id=admin.id,
        action="user_updated",
        entity_type="user",
        entity_id=user.id,
        meta=data,
    )
    db.commit()
    db.refresh(user)
    return user


def dashboard_summary(db: Session):
    users = db.query(User).count()
    sellers_pending = db.query(SellerProfile).filter(SellerProfile.approval_status == "pending").count()
    sellers_approved = db.query(SellerProfile).filter(SellerProfile.approval_status == "approved").count()
    orders = db.query(Order).count()
    delivered_orders = db.query(Order).filter(Order.order_status == "delivered").all()
    revenue = sum((order.total_amount or 0) for order in delivered_orders)
    return DashboardSummaryResponse(
        users=users,
        sellers_pending=sellers_pending,
        sellers_approved=sellers_approved,
        orders=orders,
        revenue=Decimal(revenue or 0),
    )


def list_audit_logs(db: Session, limit: int = 100):
    return audit_repository.list_audit_logs(db, limit=limit)

