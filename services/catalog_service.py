"""Catalog, inventory, and buyer marketplace business logic."""
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import SellerProduct, User
from repositories import audit_repository, catalog_repository
from schemas.product_schemas import (
    BrandCreate,
    BrandUpdate,
    CategoryCreate,
    CategoryUpdate,
    MasterProductCreate,
    MasterProductUpdate,
    ProductImageCreate,
    SellerProductCreate,
    SellerProductUpdate,
)
from schemas.marketplace_schemas import (
    MasterProductWithOffersResponse,
    ProductSearchResponse,
    SellerOfferResponse,
)
from services import seller_service
from utils.constants import SELLER_PRODUCT_STATUSES


def _dump(payload):
    return payload.model_dump(exclude_unset=True)


def _seller_product_response(product: SellerProduct) -> ProductSearchResponse:
    master = product.master_product
    seller = product.seller
    return ProductSearchResponse(
        id=product.id,
        seller_id=product.seller_id,
        master_product_id=product.master_product_id,
        product_name=master.product_name,
        category_name=master.category.name if master.category else None,
        brand_name=master.brand.name if master.brand else None,
        business_name=seller.business_name,
        seller_type=seller.seller_type,
        price=product.price,
        discounted_price=product.discounted_price,
        stock_quantity=product.stock_quantity,
        moq=product.moq,
        delivery_radius_km=product.delivery_radius_km,
        lead_time_days=int(product.lead_time_days) if product.lead_time_days is not None else None,
        status=product.status,
    )


def list_public_products(db: Session, search=None, category_id: UUID | None = None, brand_id: UUID | None = None):
    products = catalog_repository.list_public_seller_products(
        db, search=search, category_id=category_id, brand_id=brand_id
    )
    return [_seller_product_response(product) for product in products]


def get_marketplace_product_detail(db: Session, master_product_id: UUID):
    product = catalog_repository.get_master_product(db, master_product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    offers = catalog_repository.list_public_seller_products(db, seller_id=None)
    filtered = [offer for offer in offers if offer.master_product_id == master_product_id]
    return MasterProductWithOffersResponse(
        id=product.id,
        product_name=product.product_name,
        description=product.description,
        base_unit=product.base_unit,
        category_name=product.category.name if product.category else None,
        brand_name=product.brand.name if product.brand else None,
        offers=[SellerOfferResponse(**_seller_product_response(offer).model_dump()) for offer in filtered],
    )


def create_category(db: Session, admin: User, payload: CategoryCreate):
    category = catalog_repository.create_category(db, payload.model_dump())
    audit_repository.create_audit_log(db, user_id=admin.id, action="category_created", entity_type="category", entity_id=category.id)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, admin: User, category_id: UUID, payload: CategoryUpdate):
    category = catalog_repository.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category = catalog_repository.update_category(db, category, payload.model_dump(exclude_unset=True))
    audit_repository.create_audit_log(db, user_id=admin.id, action="category_updated", entity_type="category", entity_id=category.id)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, admin: User, category_id: UUID):
    category = catalog_repository.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    catalog_repository.delete_category(db, category)
    audit_repository.create_audit_log(db, user_id=admin.id, action="category_deleted", entity_type="category", entity_id=category_id)
    db.commit()


def create_brand(db: Session, admin: User, payload: BrandCreate):
    brand = catalog_repository.create_brand(db, payload.model_dump())
    audit_repository.create_audit_log(db, user_id=admin.id, action="brand_created", entity_type="brand", entity_id=brand.id)
    db.commit()
    db.refresh(brand)
    return brand


def update_brand(db: Session, admin: User, brand_id: UUID, payload: BrandUpdate):
    brand = catalog_repository.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    brand = catalog_repository.update_brand(db, brand, payload.model_dump(exclude_unset=True))
    audit_repository.create_audit_log(db, user_id=admin.id, action="brand_updated", entity_type="brand", entity_id=brand.id)
    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(db: Session, admin: User, brand_id: UUID):
    brand = catalog_repository.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    catalog_repository.delete_brand(db, brand)
    audit_repository.create_audit_log(db, user_id=admin.id, action="brand_deleted", entity_type="brand", entity_id=brand_id)
    db.commit()


def create_master_product(db: Session, admin: User, payload: MasterProductCreate):
    if not catalog_repository.get_category(db, payload.category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    if payload.brand_id and not catalog_repository.get_brand(db, payload.brand_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand not found")
    product = catalog_repository.create_master_product(db, payload.model_dump())
    audit_repository.create_audit_log(db, user_id=admin.id, action="master_product_created", entity_type="master_product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def update_master_product(db: Session, admin: User, product_id: UUID, payload: MasterProductUpdate):
    product = catalog_repository.get_master_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Master product not found")
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and not catalog_repository.get_category(db, data["category_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")
    if data.get("brand_id") and not catalog_repository.get_brand(db, data["brand_id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand not found")
    product = catalog_repository.update_master_product(db, product, data)
    audit_repository.create_audit_log(db, user_id=admin.id, action="master_product_updated", entity_type="master_product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def deactivate_master_product(db: Session, admin: User, product_id: UUID):
    product = catalog_repository.get_master_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Master product not found")
    product = catalog_repository.update_master_product(db, product, {"is_active": False})
    audit_repository.create_audit_log(db, user_id=admin.id, action="master_product_deactivated", entity_type="master_product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def create_my_seller_product(db: Session, user: User, payload: SellerProductCreate):
    seller = seller_service.ensure_approved_seller(db, user)
    if not catalog_repository.get_master_product(db, payload.master_product_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Master product not found")
    data = payload.model_dump()
    data["seller_id"] = seller.id
    product = catalog_repository.create_seller_product(db, data)
    audit_repository.create_audit_log(db, user_id=user.id, action="seller_product_created", entity_type="seller_product", entity_id=product.id)
    db.commit()
    db.refresh(product)
    return product


def list_my_seller_products(db: Session, user: User):
    seller = seller_service.get_my_seller_profile(db, user)
    return catalog_repository.list_seller_products(db, seller.id)


def update_my_seller_product(db: Session, user: User, seller_product_id: UUID, payload: SellerProductUpdate):
    seller = seller_service.get_my_seller_profile(db, user)
    product = catalog_repository.get_seller_product(db, seller_product_id)
    if not product or product.seller_id != seller.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller product not found")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in SELLER_PRODUCT_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product status")
    product = catalog_repository.update_seller_product(db, product, data)
    audit_repository.create_audit_log(db, user_id=user.id, action="seller_product_updated", entity_type="seller_product", entity_id=product.id, meta=data)
    db.commit()
    db.refresh(product)
    return product


def delete_my_seller_product(db: Session, user: User, seller_product_id: UUID):
    seller = seller_service.get_my_seller_profile(db, user)
    product = catalog_repository.get_seller_product(db, seller_product_id)
    if not product or product.seller_id != seller.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller product not found")
    catalog_repository.delete_seller_product(db, product)
    audit_repository.create_audit_log(db, user_id=user.id, action="seller_product_deleted", entity_type="seller_product", entity_id=seller_product_id)
    db.commit()


def add_my_product_image(db: Session, user: User, seller_product_id: UUID, payload: ProductImageCreate):
    seller = seller_service.get_my_seller_profile(db, user)
    product = catalog_repository.get_seller_product(db, seller_product_id)
    if not product or product.seller_id != seller.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller product not found")
    image = catalog_repository.create_product_image(db, {"seller_product_id": seller_product_id, **payload.model_dump()})
    audit_repository.create_audit_log(db, user_id=user.id, action="product_image_created", entity_type="seller_product", entity_id=seller_product_id)
    db.commit()
    db.refresh(image)
    return image


def delete_my_product_image(db: Session, user: User, seller_product_id: UUID, image_id: UUID):
    seller = seller_service.get_my_seller_profile(db, user)
    product = catalog_repository.get_seller_product(db, seller_product_id)
    image = catalog_repository.get_product_image(db, image_id)
    if not product or product.seller_id != seller.id or not image or image.seller_product_id != seller_product_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product image not found")
    catalog_repository.delete_product_image(db, image)
    audit_repository.create_audit_log(db, user_id=user.id, action="product_image_deleted", entity_type="seller_product", entity_id=seller_product_id)
    db.commit()
