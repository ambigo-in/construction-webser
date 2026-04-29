"""Buyer marketplace product routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.marketplace_schemas import MasterProductWithOffersResponse, ProductSearchResponse
from services import catalog_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductSearchResponse])
def list_products(
    search: Optional[str] = Query(default=None),
    category_id: Optional[UUID] = Query(default=None),
    brand_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
):
    return catalog_service.list_public_products(db, search=search, category_id=category_id, brand_id=brand_id)


@router.get("/{master_product_id}", response_model=MasterProductWithOffersResponse)
def product_detail(master_product_id: UUID, db: Session = Depends(get_db)):
    return catalog_service.get_marketplace_product_detail(db, master_product_id)

