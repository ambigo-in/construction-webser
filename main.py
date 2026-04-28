from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import get_db, init_db
from routers.auth import router as auth_router
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


# ============================================
# ROUTE PLACEHOLDERS (to be implemented)
# ============================================

# TODO: User routes
# TODO: Product routes  
# TODO: Cart routes
# TODO: Order routes
# TODO: Payment routes
# TODO: Delivery routes
# TODO: Review routes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
