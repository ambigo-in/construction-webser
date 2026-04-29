"""Seller onboarding and dashboard business logic."""
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from repositories import audit_repository, seller_repository
from schemas.seller_schemas import SellerProfileCreate, SellerProfileUpdate
from schemas.marketplace_schemas import SellerDashboardResponse
from utils.constants import SELLER_APPROVAL_STATUSES, SELLER_ROLES


def _role_names(user: User) -> set[str]:
    return {role.role_name.lower() for role in (user.roles or [])}


def require_seller_role(user: User) -> None:
    if not (_role_names(user) & SELLER_ROLES):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller role required")


def get_my_seller_profile(db: Session, user: User):
    require_seller_role(user)
    seller = seller_repository.get_seller_by_user_id(db, user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
    return seller


def create_my_seller_profile(db: Session, user: User, payload: SellerProfileCreate):
    require_seller_role(user)
    existing = seller_repository.get_seller_by_user_id(db, user.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Seller profile already exists")

    seller_type = (payload.seller_type or next(iter(_role_names(user) & SELLER_ROLES), "retailer")).lower()
    if seller_type not in SELLER_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="seller_type must be retailer or wholesaler")

    seller = seller_repository.create_seller_profile(
        db,
        {
            **payload.model_dump(exclude={"seller_type"}),
            "seller_type": seller_type,
            "user_id": user.id,
            "approval_status": "pending",
        },
    )
    audit_repository.create_audit_log(
        db,
        user_id=user.id,
        action="seller_profile_created",
        entity_type="seller",
        entity_id=seller.id,
        meta={"approval_status": seller.approval_status},
    )
    db.commit()
    db.refresh(seller)
    return seller


def update_my_seller_profile(db: Session, user: User, payload: SellerProfileUpdate):
    seller = get_my_seller_profile(db, user)
    data = payload.model_dump(exclude_unset=True)
    data.pop("commission_rate", None)
    seller = seller_repository.update_seller_profile(db, seller, data)
    audit_repository.create_audit_log(
        db,
        user_id=user.id,
        action="seller_profile_updated",
        entity_type="seller",
        entity_id=seller.id,
        meta=data,
    )
    db.commit()
    db.refresh(seller)
    return seller


def ensure_approved_seller(db: Session, user: User):
    seller = get_my_seller_profile(db, user)
    if seller.approval_status != "approved":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seller profile is not approved")
    return seller


def list_sellers(db: Session, approval_status: str | None = None):
    if approval_status and approval_status not in SELLER_APPROVAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid approval_status")
    return seller_repository.list_sellers(db, approval_status=approval_status)


def approve_seller(db: Session, admin: User, seller_id, approval_status: str):
    if approval_status not in SELLER_APPROVAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid approval_status")
    seller = seller_repository.get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    seller = seller_repository.update_seller_profile(db, seller, {"approval_status": approval_status})
    audit_repository.create_audit_log(
        db,
        user_id=admin.id,
        action="seller_approval_updated",
        entity_type="seller",
        entity_id=seller.id,
        meta={"approval_status": approval_status},
    )
    db.commit()
    db.refresh(seller)
    return seller


def update_seller_commission(db: Session, admin: User, seller_id, commission_rate: Decimal):
    seller = seller_repository.get_seller(db, seller_id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    seller = seller_repository.update_seller_profile(db, seller, {"commission_rate": commission_rate})
    audit_repository.create_audit_log(
        db,
        user_id=admin.id,
        action="seller_commission_updated",
        entity_type="seller",
        entity_id=seller.id,
        meta={"commission_rate": str(commission_rate)},
    )
    db.commit()
    db.refresh(seller)
    return seller


def get_seller_dashboard(db: Session, user: User) -> SellerDashboardResponse:
    seller = get_my_seller_profile(db, user)
    active, pending, completed, revenue = seller_repository.seller_dashboard_counts(db, seller.id)
    return SellerDashboardResponse(
        active_products=active,
        pending_orders=pending,
        completed_orders=completed,
        revenue=Decimal(revenue or 0),
    )

