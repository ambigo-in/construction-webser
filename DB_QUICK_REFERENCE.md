# 🗄️ Database Quick Reference Guide

## Table Relationships Map

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ full_name       │
│ email (UNIQUE)  │
│ phone (UNIQUE)  │
│ password_hash   │
│ is_verified     │
│ is_active       │
└────────┬────────┘
         │
    ┌────┴──────────────────────────────┐
    │                                   │
┌───▼──────────┐  ┌──────────────┐  ┌──▼──────────────┐
│  USER_ROLES  │  │  ADDRESSES   │  │ SELLER_PROFILES│
│  (M-to-M)    │  ├──────────────┤  ├─────────────────┤
└──────────────┘  │ id (FK→users)│  │ id              │
    │      │     │ type         │  │ user_id (FK)    │
    │      │     │ line1        │  │ business_name   │
┌───▼──┐ ┌─▼──┐  │ city         │  │ gst_number      │
│ROLES │ │    │  │ pincode      │  │ approval_status │
│      │ │    │  │ lat/long     │  └────────┬────────┘
└──────┘ └────┘  └──────────────┘           │
                                            │
                                    ┌───────▼────────┐
                                    │ SELLER_PRODUCTS│
                                    ├────────────────┤
                                    │ seller_id (FK) │
                                    │ master_id (FK) │
                                    │ price          │
                                    │ stock_qty      │
                                    │ moq            │
                                    │ status         │
                                    └────────┬───────┘
                                            │
                        ┌───────────────────┴───────────────┐
                        │                                   │
                    ┌───▼──────────┐          ┌────────────▼──┐
                    │ PRODUCT_     │          │ CART_ITEMS    │
                    │ IMAGES       │          ├───────────────┤
                    ├──────────────┤          │ seller_prod_id│
                    │ image_url    │          │ quantity      │
                    │ is_primary   │          └───────────────┘
                    └──────────────┘


┌──────────────────────┐
│  MASTER_PRODUCTS     │
├──────────────────────┤
│ id (PK)              │
│ category_id (FK)     │◄─────┐
│ brand_id (FK)        │      │ (FK)
│ product_name         │      │
│ base_unit            │  ┌───┴──────────┐  ┌──────────────┐
│ weight_per_unit      │  │  CATEGORIES  │  │    BRANDS    │
│ dimensions (JSON)    │  ├──────────────┤  ├──────────────┤
│ is_active            │  │ parent_id    │  │ name         │
└──────────────────────┘  │ name         │  │ logo_url     │
                          └──────────────┘  └──────────────┘


┌─────────────────┐      ┌──────────────┐
│  CARTS          │      │  CART_ITEMS  │
├─────────────────┤      ├──────────────┤
│ id              │◄─────│ cart_id (FK) │
│ user_id (FK)    │      │ seller_prod  │
└─────────────────┘      │ quantity     │
                         └──────────────┘


┌──────────────────┐
│  ORDERS          │
├──────────────────┤          ┌──────────────────┐
│ id               │◄─────────│  ORDER_ITEMS     │
│ buyer_id (FK)    │          ├──────────────────┤
│ seller_id (FK)   │          │ order_id (FK)    │
│ delivery_addr(FK)│          │ seller_prod(FK)  │
│ order_status     │          │ quantity         │
│ payment_status   │          │ unit_price       │
│ total_amount     │          │ tax_rate         │
└────────┬─────────┘          │ total_price      │
         │                    └──────────────────┘
    ┌────┴──────────────┬──────────────┐
    │                   │              │
┌───▼───────┐  ┌────────▼────┐  ┌────▼──────────┐
│ PAYMENTS  │  │ DELIVERIES  │  │ SELLER_PAYOUTS│
├───────────┤  ├─────────────┤  ├───────────────┤
│ order_id  │  │ order_id    │  │ seller_id (FK)│
│ gateway   │  │ agent_id    │  │ order_id (FK) │
│ amount    │  │ status      │  │ gross_amount  │
│ status    │  │ otp_verify  │  │ commission    │
└───────────┘  │ notes       │  │ net_payout    │
               └─────────────┘  │ payout_status │
                                └───────────────┘


┌─────────────────┐
│ NOTIFICATIONS   │
├─────────────────┤
│ user_id (FK)    │
│ type            │
│ title           │
│ message         │
│ is_read         │
└─────────────────┘


┌─────────────────┐      ┌──────────────────┐
│  REVIEWS        │      │  AUDIT_LOGS      │
├─────────────────┤      ├──────────────────┤
│ id              │      │ user_id (FK)     │
│ order_id (FK)   │      │ action           │
│ buyer_id (FK)   │      │ entity_type      │
│ seller_id (FK)  │      │ entity_id        │
│ rating (1-5)    │      │ metadata (JSON)  │
│ review_text     │      │ created_at       │
└─────────────────┘      └──────────────────┘


┌──────────────────┐
│ DELIVERY_AGENTS  │
├──────────────────┤
│ id               │
│ user_id (FK)     │
│ vehicle_type     │
│ license_number   │
│ service_radius   │
│ approval_status  │
└──────────────────┘
```

---

## 📊 Key Relationships

### One-to-Many

- User → Addresses (one user, many addresses)
- User → Orders (one buyer, many orders)
- Seller → Products (one seller, many products)
- Category → Products (one category, many products)
- Brand → Products (one brand, many products)
- Cart → CartItems (one cart, many items)
- Order → OrderItems (one order, many items)

### Many-to-Many

- User ↔ Role (through user_roles table)

### One-to-One

- User → Cart (one user, one cart)
- User → SellerProfile (one user, one seller profile)
- User → DeliveryAgent (one user, one agent)
- Order → Payment (one order, one payment)
- Order → Delivery (one order, one delivery)
- Order → SellerPayout (one order, one payout)

---

## 🔍 Common Queries

### Find all active sellers

```python
db.query(SellerProfile).filter(
    SellerProfile.approval_status == 'approved'
).all()
```

### Get seller's products with stock > 0

```python
db.query(SellerProduct).filter(
    SellerProduct.seller_id == seller_id,
    SellerProduct.stock_quantity > 0
).all()
```

### Get pending orders for a seller

```python
db.query(Order).filter(
    Order.seller_id == seller_id,
    Order.order_status == 'placed'
).all()
```

### Get completed orders with payment received

```python
db.query(Order).filter(
    Order.order_status == 'delivered',
    Order.payment_status == 'completed'
).all()
```

### Get seller's total earnings

```python
from sqlalchemy import func

earnings = db.query(func.sum(SellerPayout.net_payout)).filter(
    SellerPayout.seller_id == seller_id,
    SellerPayout.payout_status == 'completed'
).scalar()
```

### Get product reviews

```python
db.query(Review).filter(
    Review.seller_id == seller_id
).order_by(Review.created_at.desc()).all()
```

### Get user's cart summary

```python
cart = db.query(Cart).filter(Cart.user_id == user_id).first()
items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
```

### Get order details with items and payment

```python
order = db.query(Order).filter(Order.id == order_id).first()
items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
payment = db.query(Payment).filter(Payment.order_id == order_id).first()
```

---

## 🔑 Indexes

```
users:
  - email (UNIQUE)
  - phone (UNIQUE)

seller_profiles:
  - approval_status
  - gst_number (UNIQUE)

addresses:
  - user_id
  - city
  - pincode

categories:
  - name

master_products:
  - category_id
  - product_name
  - is_active

seller_products:
  - seller_id
  - status
  - sku
  - UNIQUE(seller_id, master_product_id)

orders:
  - buyer_id
  - seller_id
  - order_status
  - payment_status
  - created_at

deliveries:
  - delivery_status

notifications:
  - user_id
  - is_read

audit_logs:
  - user_id
  - entity_type, entity_id
  - created_at
```

---

## 🛡️ Foreign Key Constraints

### CASCADE (delete children when parent deleted)

- users → addresses
- users → carts
- users → notifications
- users → audit_logs
- cart → cart_items
- order → order_items
- seller_product → product_images
- seller_profile → seller_products
- delivery_agent → deliveries (driver leaves)
- order → deliveries
- order → reviews

### RESTRICT (prevent deletion if children exist)

- categories → master_products
- master_products → seller_products
- users (buyer/seller) → orders
- addresses (delivery/billing) → orders
- delivery_agents (optional) → deliveries
- seller_profiles → seller_payouts

### SET NULL (nullify FK on delete)

- brands (optional) → master_products
- seller_agents (optional) → deliveries
- users (optional) → audit_logs

---

## 📈 Performance Tips

1. **Frequently Queried Fields**: Always indexed
2. **Filter Operations**: Index foreign keys and status fields
3. **Joins**: Ensure proper FK relationships
4. **Pagination**: Use LIMIT/OFFSET with ORDER BY
5. **Denormalization**: Consider caching order totals in orders table

---

## 🔄 MVP Data Flow

```
BUYER JOURNEY:
Browse Catalog → Add to Cart → Checkout → Place Order → Payment → Delivery → Review

SELLER JOURNEY:
Create Profile → Add Products → Get Orders → Process → Delivery → Payout → Review Feedback

ADMIN JOURNEY:
Manage Sellers → Monitor Payments → Track Delivery → Process Payouts → View Analytics
```

---

## 📋 Table Statistics

| Table           | Records (MVP) | Purpose                |
| --------------- | ------------- | ---------------------- |
| users           | ~100          | All users              |
| seller_profiles | ~20           | Active sellers         |
| categories      | ~50           | Product categories     |
| brands          | ~100          | Product brands         |
| master_products | ~500          | Product catalog        |
| seller_products | ~2,000        | Multi-vendor inventory |
| orders          | ~100-1,000    | Monthly orders         |
| order_items     | ~300-3,000    | Order line items       |
| payments        | ~100-1,000    | Transactions           |
| reviews         | ~50-500       | Customer feedback      |

---

**Last Updated**: 2026-04-28  
**Database Version**: 1.0  
**Status**: MVP Ready ✅
