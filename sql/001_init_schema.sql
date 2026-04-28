-- ============================================
-- Medica Marketplace Database Setup
-- PostgreSQL Schema Creation
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. ROLES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- ============================================
-- 2. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);

-- ============================================
-- 3. USER_ROLES ASSOCIATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE(user_id, role_id)
);

-- ============================================
-- 3b. REFRESH TOKENS TABLE (rotating refresh tokens)
-- ============================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token_hash VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    replaced_by_token_id UUID,
    created_ip VARCHAR(64),
    user_agent VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked_at ON refresh_tokens(revoked_at);

-- ============================================
-- 3c. OTP CODES TABLE (server-generated OTP)
-- ============================================
CREATE TABLE IF NOT EXISTS otp_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) NOT NULL,
    purpose VARCHAR(50) NOT NULL DEFAULT 'login',
    code_hash VARCHAR(64) NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    consumed_at TIMESTAMP,
    created_ip VARCHAR(64),
    user_agent VARCHAR(255)
);

CREATE INDEX idx_otp_codes_phone ON otp_codes(phone);
CREATE INDEX idx_otp_codes_expires_at ON otp_codes(expires_at);
CREATE INDEX idx_otp_codes_consumed_at ON otp_codes(consumed_at);
CREATE INDEX idx_otp_codes_phone_expires ON otp_codes(phone, expires_at);

-- ============================================
-- 4. ADDRESSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    address_type VARCHAR(50),
    line1 TEXT NOT NULL,
    line2 TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(20),
    country VARCHAR(100),
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    contact_name VARCHAR(150),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_addresses_user_id ON addresses(user_id);
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_pincode ON addresses(pincode);

-- ============================================
-- 5. SELLER_PROFILES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS seller_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    seller_type VARCHAR(50),
    gst_number VARCHAR(50) UNIQUE,
    business_license TEXT,
    address_id UUID,
    approval_status VARCHAR(30) DEFAULT 'pending',
    commission_rate NUMERIC(5, 2) DEFAULT 5.00,
    security_deposit NUMERIC(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE SET NULL
);

CREATE INDEX idx_seller_profiles_approval_status ON seller_profiles(approval_status);
CREATE INDEX idx_seller_profiles_gst ON seller_profiles(gst_number);

-- ============================================
-- 6. CATEGORIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID,
    name VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_categories_name ON categories(name);

-- ============================================
-- 7. BRANDS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT
);

CREATE INDEX idx_brands_name ON brands(name);

-- ============================================
-- 8. MASTER_PRODUCTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS master_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID NOT NULL,
    brand_id UUID,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    base_unit VARCHAR(50) NOT NULL,
    weight_per_unit NUMERIC(10, 2),
    dimensions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL
);

CREATE INDEX idx_master_products_category ON master_products(category_id);
CREATE INDEX idx_master_products_name ON master_products(product_name);
CREATE INDEX idx_master_products_active ON master_products(is_active);

-- ============================================
-- 9. SELLER_PRODUCTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS seller_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL,
    master_product_id UUID NOT NULL,
    sku VARCHAR(100),
    price NUMERIC(12, 2) NOT NULL,
    discounted_price NUMERIC(12, 2),
    stock_quantity NUMERIC(12, 2),
    moq NUMERIC(12, 2) DEFAULT 1,
    delivery_radius_km NUMERIC(8, 2),
    lead_time_days INTEGER,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES seller_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (master_product_id) REFERENCES master_products(id) ON DELETE RESTRICT,
    UNIQUE(seller_id, master_product_id)
);

CREATE INDEX idx_seller_products_seller ON seller_products(seller_id);
CREATE INDEX idx_seller_products_status ON seller_products(status);
CREATE INDEX idx_seller_products_sku ON seller_products(sku);

-- ============================================
-- 10. PRODUCT_IMAGES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS product_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_product_id UUID NOT NULL,
    image_url TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_product_id) REFERENCES seller_products(id) ON DELETE CASCADE
);

-- ============================================
-- 11. CARTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 12. CART_ITEMS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL,
    seller_product_id UUID NOT NULL,
    quantity NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_product_id) REFERENCES seller_products(id) ON DELETE CASCADE,
    UNIQUE(cart_id, seller_product_id)
);

-- ============================================
-- 13. ORDERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id UUID NOT NULL,
    seller_id UUID NOT NULL,
    delivery_address_id UUID NOT NULL,
    billing_address_id UUID,
    order_status VARCHAR(50) DEFAULT 'placed',
    payment_status VARCHAR(50) DEFAULT 'pending',
    subtotal NUMERIC(12, 2),
    delivery_fee NUMERIC(12, 2),
    tax_amount NUMERIC(12, 2),
    commission_amount NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (seller_id) REFERENCES seller_profiles(id) ON DELETE RESTRICT,
    FOREIGN KEY (delivery_address_id) REFERENCES addresses(id) ON DELETE RESTRICT,
    FOREIGN KEY (billing_address_id) REFERENCES addresses(id) ON DELETE SET NULL
);

CREATE INDEX idx_orders_buyer ON orders(buyer_id);
CREATE INDEX idx_orders_seller ON orders(seller_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ============================================
-- 14. ORDER_ITEMS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    seller_product_id UUID NOT NULL,
    quantity NUMERIC(12, 2),
    unit_price NUMERIC(12, 2),
    tax_rate NUMERIC(5, 2),
    total_price NUMERIC(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_product_id) REFERENCES seller_products(id) ON DELETE RESTRICT
);

-- ============================================
-- 15. PAYMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID UNIQUE NOT NULL,
    gateway_provider VARCHAR(50),
    transaction_reference VARCHAR(255),
    payment_method VARCHAR(50),
    amount_paid NUMERIC(12, 2) DEFAULT 0,
    advance_paid NUMERIC(12, 2) DEFAULT 0,
    cod_balance NUMERIC(12, 2) DEFAULT 0,
    payment_status VARCHAR(50),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE INDEX idx_payments_transaction ON payments(transaction_reference);

-- ============================================
-- 16. SELLER_PAYOUTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS seller_payouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id UUID NOT NULL,
    order_id UUID UNIQUE NOT NULL,
    gross_amount NUMERIC(12, 2),
    commission_deducted NUMERIC(12, 2),
    net_payout NUMERIC(12, 2),
    payout_status VARCHAR(50),
    payout_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES seller_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE RESTRICT
);

CREATE INDEX idx_seller_payouts_seller ON seller_payouts(seller_id);
CREATE INDEX idx_seller_payouts_status ON seller_payouts(payout_status);

-- ============================================
-- 17. DELIVERY_AGENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS delivery_agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL,
    vehicle_type VARCHAR(50),
    license_number VARCHAR(100) UNIQUE,
    service_radius_km NUMERIC(8, 2),
    approval_status VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 18. DELIVERIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID UNIQUE NOT NULL,
    delivery_agent_id UUID,
    dispatch_time TIMESTAMP,
    delivered_time TIMESTAMP,
    delivery_status VARCHAR(50),
    otp_verified BOOLEAN DEFAULT FALSE,
    delivery_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (delivery_agent_id) REFERENCES delivery_agents(id) ON DELETE SET NULL
);

CREATE INDEX idx_deliveries_status ON deliveries(delivery_status);

-- ============================================
-- 19. NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    notification_type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- ============================================
-- 20. REVIEWS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL,
    buyer_id UUID NOT NULL,
    seller_id UUID NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES seller_profiles(id) ON DELETE CASCADE
);

-- ============================================
-- 21. AUDIT_LOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(255),
    entity_type VARCHAR(100),
    entity_id UUID,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ============================================
-- INSERT DEFAULT ROLES
-- ============================================
INSERT INTO roles (role_name) VALUES 
    ('buyer'),
    ('retailer'),
    ('wholesaler'),
    ('delivery_agent'),
    ('admin')
ON CONFLICT DO NOTHING;
