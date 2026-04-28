"""
Payment Models
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Payment(Base):
    """Payment transactions - supports UPI, Cards, COD, Partial payments"""
    __tablename__ = 'payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    gateway_provider = Column(String(50), nullable=True)  # 'razorpay', 'paytm', 'phonepe', 'manual'
    transaction_reference = Column(String(255), nullable=True, index=True)  # Gateway transaction ID
    payment_method = Column(String(50), nullable=True)  # 'upi', 'card', 'netbanking', 'wallet', 'cod'
    
    # Payment amounts
    amount_paid = Column(Numeric(12, 2), default=0)  # Paid via online
    advance_paid = Column(Numeric(12, 2), default=0)  # Advance payment
    cod_balance = Column(Numeric(12, 2), default=0)  # Cash on Delivery balance
    
    payment_status = Column(String(50), default='pending', index=True)  # 'pending', 'completed', 'failed', 'cancelled', 'refunded'
    
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='payment')
