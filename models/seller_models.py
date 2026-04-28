"""
Seller Profile Models
"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class SellerProfile(Base):
    """Seller-specific business information"""
    __tablename__ = 'seller_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    business_name = Column(String(255), nullable=False, index=True)
    seller_type = Column(String(50), nullable=True)  # 'retailer', 'wholesaler', 'manufacturer', 'distributor'
    gst_number = Column(String(50), unique=True, nullable=True, index=True)
    business_license = Column(Text, nullable=True)
    
    address_id = Column(UUID(as_uuid=True), ForeignKey('addresses.id', ondelete='SET NULL'), nullable=True)
    
    approval_status = Column(String(30), default='pending', index=True)  # 'pending', 'approved', 'rejected', 'suspended'
    commission_rate = Column(Numeric(5, 2), default=5.00)  # 5% default commission
    security_deposit = Column(Numeric(12, 2), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='seller_profile', foreign_keys=[user_id])
    address = relationship('Address', foreign_keys=[address_id], back_populates='seller_profile')
    seller_products = relationship('SellerProduct', back_populates='seller', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='seller', foreign_keys='Order.seller_id')
    payouts = relationship('SellerPayout', back_populates='seller')
    reviews = relationship('Review', back_populates='seller')
