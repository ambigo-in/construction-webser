"""Cart business logic."""
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from repositories import cart_repository, catalog_repository
from schemas.cart_schemas import CartItemCreate, CartItemUpdate, CartSummary


def _validate_cart_quantity(seller_product, quantity: Decimal):
    if not seller_product or seller_product.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not available")
    if seller_product.seller.approval_status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seller is not approved")
    if quantity < seller_product.moq:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Minimum order quantity is {seller_product.moq}")
    if quantity > seller_product.stock_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock")


def get_my_cart(db: Session, user: User):
    return cart_repository.get_or_create_cart(db, user.id)


def add_cart_item(db: Session, user: User, payload: CartItemCreate):
    seller_product = catalog_repository.get_seller_product(db, payload.seller_product_id)
    _validate_cart_quantity(seller_product, payload.quantity)
    cart = cart_repository.get_or_create_cart(db, user.id)
    item = cart_repository.upsert_cart_item(
        db,
        cart,
        seller_product_id=payload.seller_product_id,
        quantity=payload.quantity,
    )
    db.commit()
    db.refresh(item)
    return item


def update_cart_item(db: Session, user: User, item_id: UUID, payload: CartItemUpdate):
    cart = cart_repository.get_or_create_cart(db, user.id)
    item = cart_repository.get_cart_item(db, item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    seller_product = catalog_repository.get_seller_product(db, item.seller_product_id)
    _validate_cart_quantity(seller_product, payload.quantity)
    item = cart_repository.update_cart_item(db, item, quantity=payload.quantity)
    db.commit()
    db.refresh(item)
    return item


def delete_cart_item(db: Session, user: User, item_id: UUID):
    cart = cart_repository.get_or_create_cart(db, user.id)
    item = cart_repository.get_cart_item(db, item_id)
    if not item or item.cart_id != cart.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    cart_repository.delete_cart_item(db, item)
    db.commit()


def get_cart_summary(db: Session, user: User) -> CartSummary:
    cart = cart_repository.get_or_create_cart(db, user.id)
    subtotal = Decimal("0")
    total_quantity = Decimal("0")
    for item in cart.items:
        price = item.seller_product.discounted_price or item.seller_product.price
        subtotal += price * item.quantity
        total_quantity += item.quantity
    return CartSummary(
        id=cart.id,
        item_count=len(cart.items),
        total_quantity=total_quantity,
        subtotal=subtotal,
        tax_amount=Decimal("0"),
        total_amount=subtotal,
    )

