"""
Cart Models
"""
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Cart(Base):
    """Shopping cart for each user"""
    __tablename__ = 'carts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='cart')
    items = relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')


class CartItem(Base):
    """Items in shopping cart"""
    __tablename__ = 'cart_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('carts.id', ondelete='CASCADE'), nullable=False)
    seller_product_id = Column(UUID(as_uuid=True), ForeignKey('seller_products.id', ondelete='CASCADE'), nullable=False)
    
    quantity = Column(Numeric(12, 2), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('cart_id', 'seller_product_id', name='uq_cart_seller_product'),
    )
    
    # Relationships
    cart = relationship('Cart', back_populates='items')
    seller_product = relationship('SellerProduct', back_populates='cart_items')
