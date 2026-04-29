"""
Audit Log Models
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class AuditLog(Base):
    """Audit trail for compliance and security"""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    action = Column(String(255), nullable=False, index=True)  # 'order_placed', 'payment_completed', 'seller_approved', etc.
    entity_type = Column(String(100), nullable=True)  # 'order', 'payment', 'seller', 'user'
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # "metadata" is reserved on SQLAlchemy Declarative models, so use a different
    # Python attribute name but keep the database column name as "metadata".
    meta = Column("metadata", JSONB, nullable=True)  # Additional context
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship('User', back_populates='audit_logs')
