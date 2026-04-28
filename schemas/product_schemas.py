"""
Product Schemas: Categories, Brands, Master Products, Seller Products
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============= CATEGORY SCHEMAS =============

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryCreate(CategoryBase):
    """Create category"""
    pass


class CategoryResponse(CategoryBase):
    """Category response"""
    id: UUID
    
    class Config:
        from_attributes = True


# ============= BRAND SCHEMAS =============

class BrandBase(BaseModel):
    """Base brand schema"""
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    """Create brand"""
    pass


class BrandResponse(BrandBase):
    """Brand response"""
    id: UUID
    
    class Config:
        from_attributes = True


# ============= MASTER PRODUCT SCHEMAS =============

class MasterProductBase(BaseModel):
    """Base master product schema"""
    product_name: str
    category_id: UUID
    brand_id: Optional[UUID] = None
    description: Optional[str] = None
    base_unit: str
    weight_per_unit: Optional[Decimal] = None
    dimensions: Optional[Dict] = None


class MasterProductCreate(MasterProductBase):
    """Create master product"""
    pass


class MasterProductResponse(MasterProductBase):
    """Master product response"""
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= SELLER PRODUCT SCHEMAS =============

class SellerProductBase(BaseModel):
    """Base seller product schema"""
    master_product_id: UUID
    price: Decimal
    discounted_price: Optional[Decimal] = None
    stock_quantity: Decimal
    moq: Optional[Decimal] = 1
    delivery_radius_km: Optional[Decimal] = None
    lead_time_days: Optional[int] = None


class SellerProductCreate(SellerProductBase):
    """Create seller product"""
    pass


class SellerProductUpdate(BaseModel):
    """Update seller product"""
    price: Optional[Decimal] = None
    discounted_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    moq: Optional[Decimal] = None
    delivery_radius_km: Optional[Decimal] = None
    lead_time_days: Optional[int] = None
    status: Optional[str] = None


class SellerProductResponse(SellerProductBase):
    """Seller product response"""
    id: UUID
    seller_id: UUID
    sku: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= PRODUCT IMAGE SCHEMAS =============

class ProductImageBase(BaseModel):
    """Base product image schema"""
    image_url: str
    is_primary: Optional[bool] = False


class ProductImageCreate(ProductImageBase):
    """Create product image"""
    pass


class ProductImageResponse(ProductImageBase):
    """Product image response"""
    id: UUID
    seller_product_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
