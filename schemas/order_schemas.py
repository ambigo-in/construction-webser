"""
Order and Order Item Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============= ORDER ITEM SCHEMAS =============

class OrderItemBase(BaseModel):
    """Base order item schema"""
    seller_product_id: UUID
    quantity: Decimal
    unit_price: Decimal


class OrderItemCreate(OrderItemBase):
    """Create order item"""
    pass


class OrderItemResponse(OrderItemBase):
    """Order item response"""
    id: UUID
    order_id: UUID
    tax_rate: Decimal
    total_price: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= ORDER SCHEMAS =============

class OrderCreate(BaseModel):
    """Create order"""
    seller_id: UUID
    delivery_address_id: UUID
    billing_address_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    items: List[OrderItemCreate]
    notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Update order"""
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Order response"""
    id: UUID
    buyer_id: UUID
    seller_id: UUID
    order_status: str
    payment_status: str
    subtotal: Decimal
    delivery_fee: Decimal
    tax_amount: Decimal
    commission_amount: Optional[Decimal]
    total_amount: Decimal
    payment_method: Optional[str]
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Order with detailed information"""
    delivery_address: Optional[dict] = None
    billing_address: Optional[dict] = None
    payment_info: Optional[dict] = None
    delivery_info: Optional[dict] = None
