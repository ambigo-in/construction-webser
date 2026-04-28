"""
Pydantic Schemas - Request/Response validation
User and Role schemas
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============= ROLE SCHEMAS =============

class RoleBase(BaseModel):
    """Base role schema"""
    role_name: str


class RoleCreate(RoleBase):
    """Create role"""
    pass


class RoleResponse(RoleBase):
    """Role response"""
    id: UUID
    
    class Config:
        from_attributes = True


# ============= USER SCHEMAS =============

class UserBase(BaseModel):
    """Base user schema"""
    full_name: str
    email: Optional[EmailStr] = None
    phone: str


class UserCreate(UserBase):
    """Create user"""
    password: str
    role_ids: List[UUID] = []


class UserLogin(BaseModel):
    """User login"""
    phone: str
    password: str


class UserUpdate(BaseModel):
    """Update user"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response"""
    id: UUID
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """User profile with addresses"""
    addresses: Optional[List] = []
