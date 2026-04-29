"""Admin operations routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.deps import require_roles
from database import get_db
from models import User
from repositories import catalog_repository
from schemas.marketplace_schemas import (
    AuditLogResponse,
    DashboardSummaryResponse,
    OrderStatusUpdate,
    PaymentStatusUpdate,
    SellerApprovalUpdate,
    SellerCommissionUpdate,
)
from schemas.order_schemas import OrderResponse
from schemas.product_schemas import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MasterProductCreate,
    MasterProductResponse,
    MasterProductUpdate,
)
from schemas.seller_schemas import SellerProfileResponse
from schemas.transaction_schemas import PaymentResponse
from schemas.user_schemas import UserResponse, UserUpdate
from services import admin_service, catalog_service, order_service, payment_service, seller_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return admin_service.list_users(db)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return admin_service.update_user_status(db, admin, user_id, payload)


@router.get("/sellers", response_model=list[SellerProfileResponse])
def list_sellers(
    approval_status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return seller_service.list_sellers(db, approval_status=approval_status)


@router.patch("/sellers/{seller_id}/approval", response_model=SellerProfileResponse)
def approve_seller(
    seller_id: UUID,
    payload: SellerApprovalUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return seller_service.approve_seller(db, admin, seller_id, payload.approval_status)


@router.patch("/sellers/{seller_id}/commission", response_model=SellerProfileResponse)
def update_commission(
    seller_id: UUID,
    payload: SellerCommissionUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return seller_service.update_seller_commission(db, admin, seller_id, payload.commission_rate)


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_repository.list_categories(db)


@router.post("/categories", response_model=CategoryResponse)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.create_category(db, admin, payload)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: UUID, payload: CategoryUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.update_category(db, admin, category_id, payload)


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    catalog_service.delete_category(db, admin, category_id)


@router.get("/brands", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_repository.list_brands(db)


@router.post("/brands", response_model=BrandResponse)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.create_brand(db, admin, payload)


@router.patch("/brands/{brand_id}", response_model=BrandResponse)
def update_brand(brand_id: UUID, payload: BrandUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.update_brand(db, admin, brand_id, payload)


@router.delete("/brands/{brand_id}", status_code=204)
def delete_brand(brand_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    catalog_service.delete_brand(db, admin, brand_id)


@router.get("/master-products", response_model=list[MasterProductResponse])
def list_master_products(
    search: Optional[str] = Query(default=None),
    category_id: Optional[UUID] = Query(default=None),
    brand_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return catalog_repository.list_master_products(db, search=search, category_id=category_id, brand_id=brand_id, active_only=False)


@router.post("/master-products", response_model=MasterProductResponse)
def create_master_product(payload: MasterProductCreate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.create_master_product(db, admin, payload)


@router.patch("/master-products/{product_id}", response_model=MasterProductResponse)
def update_master_product(product_id: UUID, payload: MasterProductUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.update_master_product(db, admin, product_id, payload)


@router.delete("/master-products/{product_id}", response_model=MasterProductResponse)
def deactivate_master_product(product_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return catalog_service.deactivate_master_product(db, admin, product_id)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    order_status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return order_service.list_admin_orders(db, order_status=order_status)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: UUID, payload: OrderStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return order_service.admin_update_order_status(db, admin, order_id, payload)


@router.get("/payments", response_model=list[PaymentResponse])
def list_payments(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return payment_service.list_payments(db)


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(payment_id: UUID, payload: PaymentStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return payment_service.update_payment_status(db, admin, payment_id, payload)


@router.get("/reports/summary", response_model=DashboardSummaryResponse)
def report_summary(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return admin_service.dashboard_summary(db)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return admin_service.list_audit_logs(db, limit=limit)
