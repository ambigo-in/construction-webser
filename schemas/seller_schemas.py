"""
Seller Profile Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class SellerProfileBase(BaseModel):
    """Base seller profile schema"""
    business_name: str
    seller_type: Optional[str] = None
    gst_number: Optional[str] = None
    business_license: Optional[str] = None


class SellerProfileCreate(SellerProfileBase):
    """Create seller profile"""
    address_id: Optional[UUID] = None
    security_deposit: Optional[Decimal] = None


class SellerProfileUpdate(BaseModel):
    """Update seller profile"""
    business_name: Optional[str] = None
    seller_type: Optional[str] = None
    gst_number: Optional[str] = None
    business_license: Optional[str] = None
    address_id: Optional[UUID] = None
    commission_rate: Optional[Decimal] = None


class SellerProfileResponse(SellerProfileBase):
    """Seller profile response"""
    id: UUID
    user_id: UUID
    approval_status: str
    commission_rate: Decimal
    security_deposit: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SellerProfileDetailResponse(SellerProfileResponse):
    """Seller profile with details"""
    address: Optional[dict] = None
    product_count: Optional[int] = 0
