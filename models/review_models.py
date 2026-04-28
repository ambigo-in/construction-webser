"""
Review Models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Review(Base):
    """Order reviews and ratings"""
    __tablename__ = 'reviews'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('seller_profiles.id', ondelete='CASCADE'), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='reviews', foreign_keys=[order_id])
    buyer = relationship('User', back_populates='reviews', foreign_keys=[buyer_id])
    seller = relationship('SellerProfile', back_populates='reviews', foreign_keys=[seller_id])
