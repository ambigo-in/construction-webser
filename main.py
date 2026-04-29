from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import get_db, init_db
from routers.auth import router as auth_router
from routers.addresses import router as addresses_router
from routers.admin import router as admin_router
from routers.cart import router as cart_router
from routers.orders import router as orders_router
from routers.payments import router as payments_router
from routers.products import router as products_router
from routers.sellers import router as sellers_router
from models import (
    User, Role, Address, SellerProfile,
    Category, Brand, MasterProduct, SellerProduct, ProductImage,
    Cart, CartItem, Order, OrderItem,
    Payment, SellerPayout,
    DeliveryAgent, Delivery,
    Notification, Review, AuditLog
)

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.API_TITLE,
    description="Construction Materials Marketplace API",
    version=settings.API_VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(products_router)
app.include_router(sellers_router)
app.include_router(addresses_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Medica Marketplace API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "development",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
