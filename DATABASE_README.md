# 🏗️ Medica Marketplace - Database Design & Setup

## 📋 Overview

This is a production-ready, scalable database design for a **Construction Materials Marketplace MVP** built with:

- **PostgreSQL** - Relational database
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

---

## 🎯 Database Architecture

### Core Modules (12 domains)

1. **User Management** - Users, Roles, Authentication
2. **Seller Management** - Seller Profiles, Business Info
3. **Product Catalog** - Categories, Brands, Products
4. **Inventory** - Stock Management
5. **Cart System** - Shopping Cart
6. **Orders** - Order Management
7. **Payments** - Payment Processing (UPI, Cards, COD)
8. **Delivery** - Delivery Tracking
9. **Notifications** - User Notifications
10. **Reviews** - Product Reviews & Ratings
11. **Admin Controls** - Management & Commission
12. **Analytics/Audit** - Audit Logging

---

## 🗄️ Database Tables (21 Tables)

### 1️⃣ Identity & Access (3 tables)

#### `roles`

- Default roles: buyer, seller, wholesaler, delivery_agent, admin
- User role assignments

#### `users`

- All platform users
- Fields: id, full_name, email, phone, password_hash, is_verified, is_active
- Indexed: email, phone

#### `user_roles`

- Many-to-many relationship between users and roles
- Supports multiple roles per user

---

### 2️⃣ Addresses (1 table)

#### `addresses`

- Supports: delivery addresses, billing, warehouse, construction sites
- GPS coordinates for location tracking
- Fields: line1, line2, city, state, pincode, country, latitude, longitude
- Indexed: user_id, city, pincode

---

### 3️⃣ Seller Management (1 table)

#### `seller_profiles`

- Business information: business_name, gst_number, seller_type
- Approval workflow: pending → approved → active
- Commission tracking (default 5%)
- Security deposit tracking

---

### 4️⃣ Product Catalog (4 tables)

#### `categories`

- Hierarchical structure (parent-child relationships)
- Example: Cement → OPC/PPC

#### `brands`

- Brand information
- Logo support

#### `master_products`

- Universal product definitions (catalog)
- One "Cement 50kg" definition shared by all sellers
- Base unit, weight, dimensions (JSON)

#### `product_images`

- Multiple images per seller product
- Primary image support

---

### 5️⃣ Multi-Vendor Inventory (1 table)

#### `seller_products`

- **KEY TABLE** - Each seller's price, stock, MOQ
- Bridge between sellers and products
- Fields:
  - price, discounted_price
  - stock_quantity
  - moq (Minimum Order Quantity)
  - delivery_radius_km
  - lead_time_days
  - status: active, inactive, out_of_stock

---

### 6️⃣ Shopping Cart (2 tables)

#### `carts`

- One cart per user
- Simple cart header

#### `cart_items`

- Items in cart
- Quantity tracking
- Links to seller_products

---

### 7️⃣ Orders & Order Items (2 tables)

#### `orders`

- Main transaction record
- Buyer ↔ Seller relationship
- Status: placed, confirmed, processing, dispatched, delivered, cancelled
- Payment status: pending, completed, failed, refunded
- Financial breakdown: subtotal, tax, delivery_fee, commission, total
- Payment method: UPI, card, COD

#### `order_items`

- Line items in order
- Snapshot of price at purchase time
- Tax rate per item
- Tax calculation support

---

### 8️⃣ Payments (1 table)

#### `payments`

- Payment transaction record
- One-to-one with order
- Supports:
  - **Online**: amount_paid (UPI, Cards)
  - **COD**: cod_balance (paid at delivery)
  - **Partial**: advance_paid + balance
- Gateway: Razorpay, Paytm, PhonePe, Manual
- Status: pending, completed, failed, refunded

---

### 9️⃣ Payouts (1 table)

#### `seller_payouts`

- Tracks commission and payout per order
- Fields:
  - gross_amount (order total)
  - commission_deducted (platform fee)
  - net_payout (seller receives)
- Status: pending, processed, completed, failed

---

### 🔟 Delivery (2 tables)

#### `delivery_agents`

- Delivery personnel/partners
- Vehicle type: bike, car, van, truck
- Approval workflow
- Service radius

#### `deliveries`

- Order delivery tracking
- Dispatch time, delivery time
- Status: pending, dispatched, in_transit, delivered, failed, returned
- OTP verification for secure delivery
- Notes for delivery instructions

---

### 1️⃣1️⃣ User Engagement (2 tables)

#### `notifications`

- User notifications
- Types: order, payment, delivery, promotion, alert, system
- Read/unread tracking

#### `reviews`

- Product reviews post-delivery
- Rating: 1-5 stars
- Text review
- Seller feedback

---

### 1️⃣2️⃣ Compliance (1 table)

#### `audit_logs`

- Audit trail for compliance
- Tracks: payment updates, admin actions, seller approvals, refunds
- Metadata in JSON
- Indexed by: user_id, entity_type, created_at

---

## 📁 Project Structure

```
web-server/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration settings
├── database.py                # Database connection & session
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user_models.py         # User, Role, user_roles
│   ├── address_models.py      # Address
│   ├── seller_models.py       # SellerProfile
│   ├── product_models.py      # Category, Brand, MasterProduct, SellerProduct, ProductImage
│   ├── cart_models.py         # Cart, CartItem
│   ├── order_models.py        # Order, OrderItem
│   ├── payment_models.py      # Payment
│   ├── payout_models.py       # SellerPayout
│   ├── delivery_models.py     # DeliveryAgent, Delivery
│   ├── notification_models.py # Notification
│   ├── review_models.py       # Review
│   └── audit_models.py        # AuditLog
├── schemas/                   # Pydantic request/response schemas
│   ├── __init__.py
│   ├── user_schemas.py        # User, Role schemas
│   ├── address_schemas.py     # Address schemas
│   ├── seller_schemas.py      # Seller schemas
│   ├── product_schemas.py     # Product schemas
│   ├── cart_schemas.py        # Cart schemas
│   ├── order_schemas.py       # Order schemas
│   └── transaction_schemas.py # Payment, Delivery, Review schemas
└── sql/                       # Raw SQL migrations
    └── 001_init_schema.sql    # Complete schema setup
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up `.env` file

```env
DATABASE_URL=postgresql://username:password@localhost:5432/medica_marketplace
DATABASE_ECHO=False
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Initialize Database (Option A - Python)

```bash
python init_db.py
```

This will:

- Create all tables
- Insert default roles
- Verify setup

### 4. Initialize Database (Option B - Raw SQL)

```bash
psql -U your_user -d medica_marketplace < sql/001_init_schema.sql
```

### 5. Start FastAPI Server

```bash
python main.py
```

The server will run on `http://localhost:8000`

---

## 🔑 Key Design Decisions

### 1. **Master Product + Seller Product Split**

- **Master Product**: Universal catalog entry (e.g., "ACC Cement 50kg")
- **Seller Product**: Seller's inventory with price, stock, MOQ
- **Benefit**: Supports multi-vendor marketplace cleanly

### 2. **UUID Primary Keys**

- Better for distributed systems
- Future-proof for microservices
- Better than auto-increment integers

### 3. **Foreign Key Constraints**

- ON DELETE CASCADE: For child records (cart items, order items)
- ON DELETE RESTRICT: For critical relationships (seller → products)
- ON DELETE SET NULL: For optional references

### 4. **Indexing Strategy**

- User lookups: email, phone
- Status fields: order_status, payment_status, delivery_status
- Foreign keys: seller_id, user_id
- Temporal: created_at for time-series queries

### 5. **JSON Fields**

- `master_products.dimensions` - Flexible product specifications
- `audit_logs.metadata` - Extensible audit info
- Better than creating separate tables for semi-structured data

### 6. **Order-Level Commission**

- Commission calculated at order time
- Snapshot stored in `orders.commission_amount`
- Supports rate changes without affecting past orders

### 7. **Flexible Payments**

- Supports partial payments (advance + COD)
- Multiple payment methods
- Gateway-agnostic (Razorpay, Paytm, etc.)

---

## 🔄 Data Flow Examples

### Order Creation Flow

```
User Cart
  ↓
Cart Items (multiple seller products)
  ↓
Create Order (aggregate by seller)
  ↓
Create Order Items (line items)
  ↓
Create Payment (transaction)
  ↓
Create Delivery (logistics)
  ↓
Create Payout (seller commission calculation)
```

### Payment Flow

```
Payment Created (pending)
  ↓
Gateway Processing (UPI/Card)
  ↓
Payment Completed
  ↓
Order Status → processing
  ↓
Delivery Created
```

### Seller Payout Flow

```
Order Completed
  ↓
Calculate Commission (order.commission_rate)
  ↓
Create Payout (pending)
  ↓
Batch Processing
  ↓
Payout Status → completed
```

---

## 📊 Query Examples (SQLAlchemy)

### Get products from seller with highest rating

```python
from models import SellerProduct, Review
from sqlalchemy import func

products = db.query(SellerProduct)\
    .join(Review)\
    .filter(SellerProduct.seller_id == seller_id)\
    .group_by(SellerProduct.id)\
    .order_by(func.avg(Review.rating).desc())\
    .limit(10)\
    .all()
```

### Get pending seller payouts

```python
from models import SellerPayout

pending_payouts = db.query(SellerPayout)\
    .filter(SellerPayout.payout_status == 'pending')\
    .all()
```

### Get orders with low payment status

```python
from models import Order

pending_orders = db.query(Order)\
    .filter(Order.payment_status == 'pending')\
    .filter(Order.created_at > datetime.now() - timedelta(days=1))\
    .all()
```

---

## 🎯 MVP Implementation Order

### Phase 1 (MVP Ready)

1. ✅ Users, Roles, Authentication
2. ✅ Seller Profiles
3. ✅ Product Catalog (Categories, Brands, Master Products)
4. ✅ Seller Inventory (Seller Products)
5. ✅ Shopping Cart
6. ✅ Orders & Order Items
7. ✅ Payments
8. ✅ Seller Payouts

### Phase 2 (Scale)

1. Delivery Tracking
2. Reviews & Ratings
3. Notifications
4. Admin Dashboard
5. Analytics

### Phase 3 (Enterprise)

1. GST Invoicing
2. Bulk Pricing Tiers
3. Loyalty Programs
4. Credit Lines
5. Advanced Analytics

---

## 🔒 Security Considerations

1. **Password Hashing** - Use bcrypt/Argon2 in FastAPI
2. **JWT Tokens** - Secure authentication
3. **HTTPS Only** - All API calls must be HTTPS in production
4. **Audit Logging** - Track all sensitive operations
5. **Rate Limiting** - Prevent abuse
6. **Input Validation** - Pydantic schemas validate all inputs
7. **SQL Injection** - SQLAlchemy ORM prevents SQL injection
8. **CORS** - Configure properly in FastAPI

---

## 📈 Scalability Path

### Current (Monolith)

- Single PostgreSQL instance
- FastAPI monolith
- File uploads (local/S3)

### Next (Modular)

- Extract services: Auth, Orders, Payments
- Event bus (RabbitMQ/Kafka)
- Separate read replicas for analytics

### Future (Microservices)

- User Service
- Product Service
- Order Service
- Payment Service
- Delivery Service
- Notification Service

---

## 🛠️ Maintenance & Operations

### Regular Tasks

- Monitor table sizes
- Vacuum & analyze tables (PostgreSQL)
- Backup database daily
- Monitor slow queries
- Archive old audit logs

### Growth Considerations

- Partitioning orders by date
- Separate schema for analytics
- Read replicas for reporting
- Elasticsearch for product search

---

## 📚 Useful Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **PostgreSQL**: https://www.postgresql.org/docs
- **Pydantic**: https://docs.pydantic.dev
- **Data Modeling**: https://en.wikipedia.org/wiki/Database_normalization

---

## ❓ Questions & Notes

### Q: Why PostgreSQL over MongoDB?

**A**:

- ACID transactions (important for payments)
- Strong relationships (seller ↔ products)
- JSON support when needed
- Great for e-commerce
- Easier to reason about schema

### Q: Can I use an ORM from day 1?

**A**: Yes! SQLAlchemy handles all table creation, relationships, and queries. Raw SQL is optional.

### Q: How do I handle schema changes?

**A**:

- For MVP: Modify models + `init_db.py`
- Production: Use Alembic migrations

### Q: How do I scale payments?

**A**:

- Add payment queue (Celery/Kafka)
- Webhook handlers for gateway responses
- Idempotent payment processing

---

## 📞 Next Steps

1. ✅ Database schema ready
2. Next: Create API routes (users, products, orders)
3. Then: Authentication & Authorization
4. Then: Payment integration
5. Then: Delivery tracking

---

**Ready to build APIs? Let's go! 🚀**
