"""
User and Role Models
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

# Association table for many-to-many relationship between users and roles
user_roles_association = Table(
    'user_roles',
    Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    UniqueConstraint('user_id', 'role_id', name='uq_user_role')
)


class Role(Base):
    """User roles: buyer, seller, delivery_agent, admin, wholesaler"""
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relationships
    users = relationship('User', secondary=user_roles_association, back_populates='roles')


class User(Base):
    """Platform users: buyers, sellers, delivery agents, admins"""
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=True, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    roles = relationship('Role', secondary=user_roles_association, back_populates='users')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    addresses = relationship('Address', back_populates='user', cascade='all, delete-orphan')
    seller_profile = relationship('SellerProfile', back_populates='user', uselist=False)
    delivery_agent = relationship('DeliveryAgent', back_populates='user', uselist=False)
    cart = relationship('Cart', back_populates='user', uselist=False, cascade='all, delete-orphan')
    orders_as_buyer = relationship('Order', foreign_keys='Order.buyer_id', back_populates='buyer')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='buyer')
    audit_logs = relationship('AuditLog', back_populates='user', cascade='all, delete-orphan')
