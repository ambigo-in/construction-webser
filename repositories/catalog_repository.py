"""Catalog and seller inventory database operations."""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import Brand, Category, MasterProduct, ProductImage, SellerProduct, SellerProfile


def list_categories(db: Session):
    return db.query(Category).order_by(Category.name.asc()).all()


def get_category(db: Session, category_id: UUID):
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, data: dict):
    category = Category(**data)
    db.add(category)
    db.flush()
    return category


def update_category(db: Session, category: Category, data: dict):
    for key, value in data.items():
        setattr(category, key, value)
    db.flush()
    return category


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.flush()


def list_brands(db: Session):
    return db.query(Brand).order_by(Brand.name.asc()).all()


def get_brand(db: Session, brand_id: UUID):
    return db.query(Brand).filter(Brand.id == brand_id).first()


def create_brand(db: Session, data: dict):
    brand = Brand(**data)
    db.add(brand)
    db.flush()
    return brand


def update_brand(db: Session, brand: Brand, data: dict):
    for key, value in data.items():
        setattr(brand, key, value)
    db.flush()
    return brand


def delete_brand(db: Session, brand: Brand):
    db.delete(brand)
    db.flush()


def list_master_products(
    db: Session,
    *,
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    brand_id: Optional[UUID] = None,
    active_only: bool = True,
):
    query = db.query(MasterProduct)
    if active_only:
        query = query.filter(MasterProduct.is_active.is_(True))
    if search:
        query = query.filter(MasterProduct.product_name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(MasterProduct.category_id == category_id)
    if brand_id:
        query = query.filter(MasterProduct.brand_id == brand_id)
    return query.order_by(MasterProduct.product_name.asc()).all()


def get_master_product(db: Session, product_id: UUID):
    return db.query(MasterProduct).filter(MasterProduct.id == product_id).first()


def create_master_product(db: Session, data: dict):
    product = MasterProduct(**data)
    db.add(product)
    db.flush()
    return product


def update_master_product(db: Session, product: MasterProduct, data: dict):
    for key, value in data.items():
        setattr(product, key, value)
    db.flush()
    return product


def list_public_seller_products(
    db: Session,
    *,
    search: Optional[str] = None,
    category_id: Optional[UUID] = None,
    brand_id: Optional[UUID] = None,
    seller_id: Optional[UUID] = None,
):
    query = (
        db.query(SellerProduct)
        .join(SellerProduct.master_product)
        .join(SellerProduct.seller)
        .filter(SellerProduct.status == "active")
        .filter(SellerProduct.stock_quantity > 0)
        .filter(SellerProfile.approval_status == "approved")
        .filter(MasterProduct.is_active.is_(True))
    )
    if search:
        query = query.filter(MasterProduct.product_name.ilike(f"%{search}%"))
    if category_id:
        query = query.filter(MasterProduct.category_id == category_id)
    if brand_id:
        query = query.filter(MasterProduct.brand_id == brand_id)
    if seller_id:
        query = query.filter(SellerProduct.seller_id == seller_id)
    return query.order_by(SellerProduct.discounted_price.asc().nulls_last(), SellerProduct.price.asc()).all()


def get_seller_product(db: Session, seller_product_id: UUID):
    return db.query(SellerProduct).filter(SellerProduct.id == seller_product_id).first()


def list_seller_products(db: Session, seller_id: UUID):
    return (
        db.query(SellerProduct)
        .filter(SellerProduct.seller_id == seller_id)
        .order_by(SellerProduct.created_at.desc())
        .all()
    )


def create_seller_product(db: Session, data: dict):
    product = SellerProduct(**data)
    db.add(product)
    db.flush()
    return product


def update_seller_product(db: Session, product: SellerProduct, data: dict):
    for key, value in data.items():
        setattr(product, key, value)
    db.flush()
    return product


def delete_seller_product(db: Session, product: SellerProduct):
    db.delete(product)
    db.flush()


def create_product_image(db: Session, data: dict):
    image = ProductImage(**data)
    db.add(image)
    db.flush()
    return image


def get_product_image(db: Session, image_id: UUID):
    return db.query(ProductImage).filter(ProductImage.id == image_id).first()


def delete_product_image(db: Session, image: ProductImage):
    db.delete(image)
    db.flush()
