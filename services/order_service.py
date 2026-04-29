"""Order placement and fulfillment business logic."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Order, User
from repositories import address_repository, audit_repository, catalog_repository, order_repository, seller_repository
from schemas.marketplace_schemas import CheckoutCreate, OrderStatusUpdate
from utils.constants import ORDER_STATUS_FLOW


def _effective_price(seller_product):
    return seller_product.discounted_price or seller_product.price


def _assert_address_owner(db: Session, user: User, address_id: UUID):
    address = address_repository.get_address(db, address_id)
    if not address or address.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address")
    return address


def _validate_checkout_product(seller_product, quantity: Decimal):
    if not seller_product or seller_product.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not available")
    if seller_product.seller.approval_status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seller is not approved")
    if quantity < seller_product.moq:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Minimum order quantity is {seller_product.moq}")
    if quantity > seller_product.stock_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock")


def place_order(db: Session, user: User, payload: CheckoutCreate):
    if not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order must contain at least one item")
    _assert_address_owner(db, user, payload.delivery_address_id)
    if payload.billing_address_id:
        _assert_address_owner(db, user, payload.billing_address_id)

    seller_id = None
    order_items = []
    subtotal = Decimal("0")
    for item in payload.items:
        seller_product = catalog_repository.get_seller_product(db, item.seller_product_id)
        _validate_checkout_product(seller_product, item.quantity)
        if seller_id is None:
            seller_id = seller_product.seller_id
        elif seller_id != seller_product.seller_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MVP checkout supports one seller per order")

        unit_price = _effective_price(seller_product)
        total_price = unit_price * item.quantity
        subtotal += total_price
        order_items.append(
            {
                "seller_product_id": seller_product.id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "tax_rate": Decimal("0"),
                "total_price": total_price,
            }
        )

    seller = seller_repository.get_seller(db, seller_id)
    delivery_fee = Decimal("0")
    tax_amount = Decimal("0")
    total_amount = subtotal + delivery_fee + tax_amount
    commission_amount = subtotal * (seller.commission_rate or Decimal("0")) / Decimal("100")

    order = order_repository.create_order(
        db,
        {
            "buyer_id": user.id,
            "seller_id": seller_id,
            "delivery_address_id": payload.delivery_address_id,
            "billing_address_id": payload.billing_address_id,
            "order_status": "placed",
            "payment_status": "pending",
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "tax_amount": tax_amount,
            "commission_amount": commission_amount,
            "total_amount": total_amount,
            "payment_method": payload.payment_method,
            "notes": payload.notes,
        },
        order_items,
    )
    order_repository.create_payment(
        db,
        {
            "order_id": order.id,
            "gateway_provider": "manual" if payload.payment_method == "cod" else None,
            "payment_method": payload.payment_method,
            "amount_paid": Decimal("0"),
            "advance_paid": Decimal("0"),
            "cod_balance": total_amount if payload.payment_method == "cod" else Decimal("0"),
            "payment_status": "pending",
        },
    )
    order_repository.create_delivery(db, {"order_id": order.id, "delivery_status": "pending"})
    order_repository.create_payout(
        db,
        {
            "seller_id": seller_id,
            "order_id": order.id,
            "gross_amount": total_amount,
            "commission_deducted": commission_amount,
            "net_payout": total_amount - commission_amount,
            "payout_status": "pending",
        },
    )
    audit_repository.create_audit_log(
        db,
        user_id=user.id,
        action="order_placed",
        entity_type="order",
        entity_id=order.id,
        meta={"seller_id": str(seller_id), "total_amount": str(total_amount)},
    )
    db.commit()
    db.refresh(order)
    return order


def list_my_orders(db: Session, user: User):
    return order_repository.list_buyer_orders(db, user.id)


def get_my_order(db: Session, user: User, order_id: UUID):
    order = order_repository.get_order(db, order_id)
    if not order or order.buyer_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def list_seller_orders(db: Session, seller_user: User):
    seller = seller_repository.get_seller_by_user_id(db, seller_user.id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller profile not found")
    return order_repository.list_seller_orders(db, seller.id)


def get_seller_order(db: Session, seller_user: User, order_id: UUID):
    seller = seller_repository.get_seller_by_user_id(db, seller_user.id)
    order = order_repository.get_order(db, order_id)
    if not seller or not order or order.seller_id != seller.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def _validate_status_transition(order: Order, new_status: str):
    allowed = ORDER_STATUS_FLOW.get(order.order_status, set())
    if new_status == order.order_status:
        return
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move order from {order.order_status} to {new_status}",
        )


def _deduct_stock_for_confirmation(order: Order):
    for item in order.items:
        product = item.seller_product
        if item.quantity > product.stock_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock to confirm order")
        product.stock_quantity -= item.quantity
        if product.stock_quantity <= 0:
            product.status = "out_of_stock"


def update_seller_order_status(db: Session, seller_user: User, order_id: UUID, payload: OrderStatusUpdate):
    order = get_seller_order(db, seller_user, order_id)
    _validate_status_transition(order, payload.order_status)
    if order.order_status == "placed" and payload.order_status == "confirmed":
        _deduct_stock_for_confirmation(order)
    order = order_repository.update_order_status(db, order, status=payload.order_status, notes=payload.notes)
    delivery = order_repository.get_delivery_by_order(db, order.id)
    if delivery and payload.order_status == "dispatched":
        order_repository.update_delivery(db, delivery, {"delivery_status": "dispatched", "dispatch_time": datetime.utcnow()})
    if delivery and payload.order_status == "delivered":
        order_repository.update_delivery(db, delivery, {"delivery_status": "delivered", "delivered_time": datetime.utcnow()})
    audit_repository.create_audit_log(
        db,
        user_id=seller_user.id,
        action="order_status_updated",
        entity_type="order",
        entity_id=order.id,
        meta={"order_status": payload.order_status},
    )
    db.commit()
    db.refresh(order)
    return order


def cancel_my_order(db: Session, user: User, order_id: UUID):
    order = get_my_order(db, user, order_id)
    _validate_status_transition(order, "cancelled")
    order = order_repository.update_order_status(db, order, status="cancelled")
    audit_repository.create_audit_log(db, user_id=user.id, action="order_cancelled", entity_type="order", entity_id=order.id)
    db.commit()
    db.refresh(order)
    return order


def list_admin_orders(db: Session, order_status: str | None = None):
    return order_repository.list_orders(db, order_status=order_status)


def admin_update_order_status(db: Session, admin: User, order_id: UUID, payload: OrderStatusUpdate):
    order = order_repository.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order = order_repository.update_order_status(db, order, status=payload.order_status, notes=payload.notes)
    audit_repository.create_audit_log(
        db,
        user_id=admin.id,
        action="admin_order_status_updated",
        entity_type="order",
        entity_id=order.id,
        meta={"order_status": payload.order_status},
    )
    db.commit()
    db.refresh(order)
    return order

