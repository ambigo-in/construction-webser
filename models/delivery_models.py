"""
Delivery and Delivery Agent Models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class DeliveryAgent(Base):
    """Delivery personnel/partners"""
    __tablename__ = 'delivery_agents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    vehicle_type = Column(String(50), nullable=True)  # 'bike', 'car', 'van', 'truck'
    license_number = Column(String(100), nullable=True, unique=True)
    service_radius_km = Column(Numeric(8, 2), nullable=True)
    
    approval_status = Column(String(30), default='pending', index=True)  # 'pending', 'approved', 'rejected', 'suspended'
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='delivery_agent')
    deliveries = relationship('Delivery', back_populates='delivery_agent')


class Delivery(Base):
    """Order delivery tracking"""
    __tablename__ = 'deliveries'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), unique=True, nullable=False)
    delivery_agent_id = Column(UUID(as_uuid=True), ForeignKey('delivery_agents.id', ondelete='SET NULL'), nullable=True)
    
    dispatch_time = Column(DateTime, nullable=True)
    delivered_time = Column(DateTime, nullable=True)
    
    delivery_status = Column(String(50), default='pending', index=True)  # 'pending', 'dispatched', 'in_transit', 'delivered', 'failed', 'returned'
    otp_verified = Column(Boolean, default=False)  # OTP verification for delivery
    
    delivery_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='delivery')
    delivery_agent = relationship('DeliveryAgent', back_populates='deliveries')
