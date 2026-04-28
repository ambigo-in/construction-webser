"""
Address Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class AddressBase(BaseModel):
    """Base address schema"""
    address_type: Optional[str] = None
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class AddressCreate(AddressBase):
    """Create address"""
    pass


class AddressUpdate(BaseModel):
    """Update address"""
    address_type: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class AddressResponse(AddressBase):
    """Address response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
