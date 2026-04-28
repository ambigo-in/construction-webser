"""
Notification Models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Notification(Base):
    """User notifications: order updates, promotions, alerts"""
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    notification_type = Column(String(50), nullable=True)  # 'order', 'payment', 'delivery', 'promotion', 'alert', 'system'
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    is_read = Column(Boolean, default=False, index=True)
    
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='notifications')
