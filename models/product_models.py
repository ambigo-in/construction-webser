"""
Product Catalog Models: Categories, Brands, Products, Images
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class Category(Base):
    """Hierarchical product categories"""
    __tablename__ = 'categories'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    
    name = Column(String(150), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    parent = relationship('Category', remote_side=[id], backref='subcategories')
    master_products = relationship('MasterProduct', back_populates='category')


class Brand(Base):
    """Product brands"""
    __tablename__ = 'brands'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    
    # Relationships
    master_products = relationship('MasterProduct', back_populates='brand')


class MasterProduct(Base):
    """Universal product definitions (catalog)"""
    __tablename__ = 'master_products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='SET NULL'), nullable=True)
    
    product_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    base_unit = Column(String(50), nullable=False)  # 'bag', 'liter', 'box', 'piece', 'kg', 'meter', etc.
    weight_per_unit = Column(Numeric(10, 2), nullable=True)  # Weight in kg
    dimensions = Column(JSONB, nullable=True)  # Stored as JSON: {length, width, height, unit}
    
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship('Category', back_populates='master_products')
    brand = relationship('Brand', back_populates='master_products')
    seller_products = relationship('SellerProduct', back_populates='master_product', cascade='all, delete-orphan')


class SellerProduct(Base):
    """Multi-vendor product inventory: each seller's price, stock, MOQ"""
    __tablename__ = 'seller_products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey('seller_profiles.id', ondelete='CASCADE'), nullable=False)
    master_product_id = Column(UUID(as_uuid=True), ForeignKey('master_products.id', ondelete='RESTRICT'), nullable=False)
    
    sku = Column(String(100), nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=False)  # Base price
    discounted_price = Column(Numeric(12, 2), nullable=True)  # Current selling price
    stock_quantity = Column(Numeric(12, 2), nullable=False, default=0)
    
    moq = Column(Numeric(12, 2), default=1)  # Minimum Order Quantity
    delivery_radius_km = Column(Numeric(8, 2), nullable=True)  # Service radius
    lead_time_days = Column(Numeric, nullable=True)  # Days to deliver
    
    status = Column(String(30), default='active', index=True)  # 'active', 'inactive', 'out_of_stock'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('seller_id', 'master_product_id', name='uq_seller_product'),
    )
    
    # Relationships
    seller = relationship('SellerProfile', back_populates='seller_products', foreign_keys=[seller_id])
    master_product = relationship('MasterProduct', back_populates='seller_products', foreign_keys=[master_product_id])
    images = relationship('ProductImage', back_populates='seller_product', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='seller_product')
    order_items = relationship('OrderItem', back_populates='seller_product')


class ProductImage(Base):
    """Product images for seller products"""
    __tablename__ = 'product_images'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_product_id = Column(UUID(as_uuid=True), ForeignKey('seller_products.id', ondelete='CASCADE'), nullable=False)
    
    image_url = Column(Text, nullable=False)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    seller_product = relationship('SellerProduct', back_populates='images')
