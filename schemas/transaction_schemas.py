"""
Payment, Payout, Delivery and Review Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============= PAYMENT SCHEMAS =============

class PaymentBase(BaseModel):
    """Base payment schema"""
    payment_method: Optional[str] = None
    amount_paid: Optional[Decimal] = Decimal('0')
    advance_paid: Optional[Decimal] = Decimal('0')
    cod_balance: Optional[Decimal] = Decimal('0')


class PaymentCreate(PaymentBase):
    """Create payment"""
    order_id: UUID


class PaymentUpdate(BaseModel):
    """Update payment"""
    payment_status: Optional[str] = None
    transaction_reference: Optional[str] = None
    amount_paid: Optional[Decimal] = None


class PaymentResponse(PaymentBase):
    """Payment response"""
    id: UUID
    order_id: UUID
    gateway_provider: Optional[str]
    transaction_reference: Optional[str]
    payment_status: str
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= PAYOUT SCHEMAS =============

class PayoutResponse(BaseModel):
    """Payout response"""
    id: UUID
    seller_id: UUID
    order_id: UUID
    gross_amount: Decimal
    commission_deducted: Decimal
    net_payout: Decimal
    payout_status: str
    payout_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= DELIVERY AGENT SCHEMAS =============

class DeliveryAgentBase(BaseModel):
    """Base delivery agent schema"""
    vehicle_type: Optional[str] = None
    license_number: Optional[str] = None
    service_radius_km: Optional[Decimal] = None


class DeliveryAgentCreate(DeliveryAgentBase):
    """Create delivery agent"""
    pass


class DeliveryAgentResponse(DeliveryAgentBase):
    """Delivery agent response"""
    id: UUID
    user_id: UUID
    approval_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= DELIVERY SCHEMAS =============

class DeliveryCreate(BaseModel):
    """Create delivery"""
    delivery_agent_id: Optional[UUID] = None


class DeliveryUpdate(BaseModel):
    """Update delivery"""
    delivery_status: Optional[str] = None
    delivery_notes: Optional[str] = None
    otp_verified: Optional[bool] = None


class DeliveryResponse(BaseModel):
    """Delivery response"""
    id: UUID
    order_id: UUID
    delivery_agent_id: Optional[UUID]
    dispatch_time: Optional[datetime]
    delivered_time: Optional[datetime]
    delivery_status: str
    otp_verified: bool
    delivery_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= REVIEW SCHEMAS =============

class ReviewBase(BaseModel):
    """Base review schema"""
    rating: int  # 1-5
    review_text: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Create review"""
    order_id: UUID


class ReviewResponse(ReviewBase):
    """Review response"""
    id: UUID
    order_id: UUID
    buyer_id: UUID
    seller_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
