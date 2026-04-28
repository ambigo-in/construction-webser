"""
Seller Payout Models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class SellerPayout(Base):
    """Seller commission and payout tracking"""
    __tablename__ = 'seller_payouts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('seller_profiles.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='RESTRICT'), nullable=False, unique=True)
    
    gross_amount = Column(Numeric(12, 2), nullable=False)  # Total order value
    commission_deducted = Column(Numeric(12, 2), nullable=False)  # Platform commission
    net_payout = Column(Numeric(12, 2), nullable=False)  # Seller receives this amount
    
    payout_status = Column(String(50), default='pending', index=True)  # 'pending', 'processed', 'completed', 'failed'
    payout_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    seller = relationship('SellerProfile', back_populates='payouts', foreign_keys=[seller_id])
    order = relationship('Order', back_populates='payout', foreign_keys=[order_id])
