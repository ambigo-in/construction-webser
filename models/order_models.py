"""
Order Models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Order(Base):
    """Main order transaction records"""
    __tablename__ = 'orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('seller_profiles.id', ondelete='RESTRICT'), nullable=False)
    
    delivery_address_id = Column(UUID(as_uuid=True), ForeignKey('addresses.id', ondelete='RESTRICT'), nullable=False)
    billing_address_id = Column(UUID(as_uuid=True), ForeignKey('addresses.id', ondelete='SET NULL'), nullable=True)
    
    order_status = Column(String(50), default='placed', index=True)  # 'placed', 'confirmed', 'processing', 'dispatched', 'delivered', 'cancelled', 'returned'
    payment_status = Column(String(50), default='pending', index=True)  # 'pending', 'completed', 'failed', 'refunded'
    
    # Financial details
    subtotal = Column(Numeric(12, 2), nullable=False)
    delivery_fee = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    commission_amount = Column(Numeric(12, 2), nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=False)
    
    payment_method = Column(String(50), nullable=True)  # 'upi', 'card', 'cod', 'bank_transfer'
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    buyer = relationship('User', back_populates='orders_as_buyer', foreign_keys=[buyer_id])
    seller = relationship('SellerProfile', back_populates='orders', foreign_keys=[seller_id])
    delivery_address = relationship('Address', foreign_keys=[delivery_address_id], back_populates='orders_delivery')
    billing_address = relationship('Address', foreign_keys=[billing_address_id], back_populates='orders_billing')
    
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payment = relationship('Payment', back_populates='order', uselist=False, cascade='all, delete-orphan')
    delivery = relationship('Delivery', back_populates='order', uselist=False, cascade='all, delete-orphan')
    payout = relationship('SellerPayout', back_populates='order', uselist=False, cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='order', cascade='all, delete-orphan')


class OrderItem(Base):
    """Individual items in an order"""
    __tablename__ = 'order_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    seller_product_id = Column(UUID(as_uuid=True), ForeignKey('seller_products.id', ondelete='RESTRICT'), nullable=False)
    
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)  # Price at time of purchase
    tax_rate = Column(Numeric(5, 2), default=0)  # GST rate
    total_price = Column(Numeric(12, 2), nullable=False)  # quantity * unit_price + tax
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='items')
    seller_product = relationship('SellerProduct', back_populates='order_items')
