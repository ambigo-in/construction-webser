"""Schemas for marketplace-specific API responses and checkout payloads."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductSearchResponse(BaseModel):
    id: UUID
    seller_id: UUID
    master_product_id: UUID
    product_name: str
    category_name: Optional[str] = None
    brand_name: Optional[str] = None
    business_name: str
    seller_type: Optional[str] = None
    price: Decimal
    discounted_price: Optional[Decimal] = None
    stock_quantity: Decimal
    moq: Decimal
    delivery_radius_km: Optional[Decimal] = None
    lead_time_days: Optional[int] = None
    status: str


class SellerOfferResponse(ProductSearchResponse):
    pass


class MasterProductWithOffersResponse(BaseModel):
    id: UUID
    product_name: str
    description: Optional[str] = None
    base_unit: str
    category_name: Optional[str] = None
    brand_name: Optional[str] = None
    offers: List[SellerOfferResponse] = []


class CheckoutItemCreate(BaseModel):
    seller_product_id: UUID
    quantity: Decimal = Field(gt=0)


class CheckoutCreate(BaseModel):
    delivery_address_id: UUID
    billing_address_id: Optional[UUID] = None
    payment_method: Optional[str] = "cod"
    items: List[CheckoutItemCreate]
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    order_status: str
    notes: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    payment_status: str
    transaction_reference: Optional[str] = None
    amount_paid: Optional[Decimal] = None


class SellerApprovalUpdate(BaseModel):
    approval_status: str


class SellerCommissionUpdate(BaseModel):
    commission_rate: Decimal = Field(ge=0)


class DashboardSummaryResponse(BaseModel):
    users: int
    sellers_pending: int
    sellers_approved: int
    orders: int
    revenue: Decimal


class SellerDashboardResponse(BaseModel):
    active_products: int
    pending_orders: int
    completed_orders: int
    revenue: Decimal


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    meta: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
