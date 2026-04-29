"""Seller onboarding, inventory, and order routes."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user, require_roles
from database import get_db
from models import User
from schemas.marketplace_schemas import OrderStatusUpdate, SellerDashboardResponse
from schemas.order_schemas import OrderResponse
from schemas.product_schemas import ProductImageCreate, ProductImageResponse, SellerProductCreate, SellerProductResponse, SellerProductUpdate
from schemas.seller_schemas import SellerProfileCreate, SellerProfileResponse, SellerProfileUpdate
from services import catalog_service, order_service, seller_service

router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/profile", response_model=SellerProfileResponse)
def create_profile(payload: SellerProfileCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return seller_service.create_my_seller_profile(db, user, payload)


@router.get("/profile", response_model=SellerProfileResponse)
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return seller_service.get_my_seller_profile(db, user)


@router.patch("/profile", response_model=SellerProfileResponse)
def update_profile(payload: SellerProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return seller_service.update_my_seller_profile(db, user, payload)


@router.get("/dashboard", response_model=SellerDashboardResponse)
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return seller_service.get_seller_dashboard(db, user)


@router.post("/products", response_model=SellerProductResponse)
def create_product(
    payload: SellerProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    return catalog_service.create_my_seller_product(db, user, payload)


@router.get("/products", response_model=list[SellerProductResponse])
def list_products(db: Session = Depends(get_db), user: User = Depends(require_roles("retailer", "wholesaler"))):
    return catalog_service.list_my_seller_products(db, user)


@router.patch("/products/{seller_product_id}", response_model=SellerProductResponse)
def update_product(
    seller_product_id: UUID,
    payload: SellerProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    return catalog_service.update_my_seller_product(db, user, seller_product_id, payload)


@router.delete("/products/{seller_product_id}", status_code=204)
def delete_product(
    seller_product_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    catalog_service.delete_my_seller_product(db, user, seller_product_id)


@router.post("/products/{seller_product_id}/images", response_model=ProductImageResponse)
def add_product_image(
    seller_product_id: UUID,
    payload: ProductImageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    return catalog_service.add_my_product_image(db, user, seller_product_id, payload)


@router.delete("/products/{seller_product_id}/images/{image_id}", status_code=204)
def delete_product_image(
    seller_product_id: UUID,
    image_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    catalog_service.delete_my_product_image(db, user, seller_product_id, image_id)


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(require_roles("retailer", "wholesaler"))):
    return order_service.list_seller_orders(db, user)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(require_roles("retailer", "wholesaler"))):
    return order_service.get_seller_order(db, user, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("retailer", "wholesaler")),
):
    return order_service.update_seller_order_status(db, user, order_id, payload)

