"""
Address Models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Address(Base):
    """User addresses: delivery, billing, warehouse, construction sites"""
    __tablename__ = 'addresses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    address_type = Column(String(50), nullable=True)  # 'delivery', 'billing', 'warehouse', 'construction_site'
    
    line1 = Column(Text, nullable=False)
    line2 = Column(Text, nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True, index=True)
    pincode = Column(String(20), nullable=True, index=True)
    country = Column(String(100), nullable=True)
    
    # GPS coordinates for construction sites/delivery tracking
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Delivery point contact
    contact_name = Column(String(150), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='addresses')
    seller_profile = relationship('SellerProfile', back_populates='address', foreign_keys='SellerProfile.address_id')
    orders_delivery = relationship('Order', foreign_keys='Order.delivery_address_id', back_populates='delivery_address')
    orders_billing = relationship('Order', foreign_keys='Order.billing_address_id', back_populates='billing_address')
