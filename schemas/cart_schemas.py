"""
Cart and Cart Item Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============= CART ITEM SCHEMAS =============

class CartItemBase(BaseModel):
    """Base cart item schema"""
    seller_product_id: UUID
    quantity: Decimal


class CartItemCreate(CartItemBase):
    """Create cart item"""
    pass


class CartItemUpdate(BaseModel):
    """Update cart item"""
    quantity: Decimal


class CartItemResponse(CartItemBase):
    """Cart item response"""
    id: UUID
    cart_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= CART SCHEMAS =============

class CartResponse(BaseModel):
    """Cart response"""
    id: UUID
    user_id: UUID
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    """Cart summary with totals"""
    id: UUID
    item_count: int
    total_quantity: Decimal
    subtotal: Decimal
    tax_amount: Decimal = Decimal('0')
    total_amount: Decimal
