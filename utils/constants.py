"""Shared business constants for marketplace flows."""

SELLER_ROLES = {"retailer", "wholesaler"}

SELLER_APPROVAL_STATUSES = {"pending", "approved", "rejected", "suspended"}
SELLER_PRODUCT_STATUSES = {"active", "inactive", "out_of_stock"}

ORDER_STATUS_FLOW = {
    "placed": {"confirmed", "cancelled"},
    "confirmed": {"dispatched", "cancelled"},
    "dispatched": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}

PAYMENT_STATUSES = {"pending", "completed", "failed", "cancelled", "refunded"}
DELIVERY_STATUSES = {"pending", "dispatched", "in_transit", "delivered", "failed", "returned"}

