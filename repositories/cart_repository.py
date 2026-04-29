"""Cart database operations."""
from uuid import UUID

from sqlalchemy.orm import Session

from models import Cart, CartItem


def get_or_create_cart(db: Session, user_id: UUID):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        return cart
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.flush()
    return cart


def get_cart_item(db: Session, item_id: UUID):
    return db.query(CartItem).filter(CartItem.id == item_id).first()


def get_cart_item_by_product(db: Session, cart_id: UUID, seller_product_id: UUID):
    return (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.seller_product_id == seller_product_id)
        .first()
    )


def upsert_cart_item(db: Session, cart: Cart, *, seller_product_id: UUID, quantity):
    item = get_cart_item_by_product(db, cart.id, seller_product_id)
    if item:
        item.quantity = quantity
    else:
        item = CartItem(cart_id=cart.id, seller_product_id=seller_product_id, quantity=quantity)
        db.add(item)
    db.flush()
    return item


def update_cart_item(db: Session, item: CartItem, *, quantity):
    item.quantity = quantity
    db.flush()
    return item


def delete_cart_item(db: Session, item: CartItem):
    db.delete(item)
    db.flush()

