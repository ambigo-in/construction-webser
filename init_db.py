"""
Database Initialization Script
Run this to set up the database and create all tables
"""
import sys
import os
from sqlalchemy import text
from database import engine, init_db, Base

# Import all models to register them with SQLAlchemy
from models import (
    User, Role, user_roles_association,
    Address, SellerProfile,
    Category, Brand, MasterProduct, SellerProduct, ProductImage,
    Cart, CartItem,
    Order, OrderItem,
    Payment, SellerPayout,
    DeliveryAgent, Delivery,
    Notification, Review, AuditLog
)


def create_all_tables():
    """Create all tables using SQLAlchemy ORM"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False
    return True


def insert_default_roles():
    """Insert default roles"""
    print("\nInserting default roles...")
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO roles (role_name) VALUES 
                    ('buyer'),
                    ('seller'),
                    ('wholesaler'),
                    ('delivery_agent'),
                    ('admin')
                ON CONFLICT (role_name) DO NOTHING;
            """))
            conn.commit()
            print("✓ Default roles inserted!")
    except Exception as e:
        print(f"✗ Error inserting roles: {e}")
        return False
    return True


def verify_database():
    """Verify database setup"""
    print("\nVerifying database setup...")
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"✓ Found {table_count} tables")
            
            # Check roles
            result = conn.execute(text("SELECT COUNT(*) FROM roles"))
            role_count = result.scalar()
            print(f"✓ Found {role_count} roles")
            
            return True
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def main():
    """Main initialization function"""
    print("=" * 60)
    print("Medica Marketplace Database Setup")
    print("=" * 60)
    
    # Step 1: Create tables
    if not create_all_tables():
        sys.exit(1)
    
    # Step 2: Insert default roles
    if not insert_default_roles():
        sys.exit(1)
    
    # Step 3: Verify
    if not verify_database():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Database setup completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
