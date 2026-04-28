"""
Auth schemas: OTP login/signup + token refresh.
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
import re

from schemas.user_schemas import UserResponse


E164_RE = re.compile(r"^\+[1-9]\d{7,14}$")
DIGITS_RE = re.compile(r"^\d{10}$")


class OtpRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().replace(" ", "")
        # Accept 10-digit Indian numbers or E.164 (we normalize later in service).
        if DIGITS_RE.match(v) or E164_RE.match(v) or (v.isdigit() and (len(v) == 12 and v.startswith("91"))):
            return v
        raise ValueError("phone must be 10 digits (India) or E.164 (e.g. +919876543210)")


class LoginOtpVerify(BaseModel):
    phone: str
    code: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().replace(" ", "")
        if DIGITS_RE.match(v) or E164_RE.match(v) or (v.isdigit() and (len(v) == 12 and v.startswith("91"))):
            return v
        raise ValueError("phone must be 10 digits (India) or E.164 (e.g. +919876543210)")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 4 or len(v) > 10 or not v.isdigit():
            raise ValueError("code must be a numeric OTP")
        return v


class SignupOtpVerify(BaseModel):
    phone: str
    code: str
    full_name: str
    email: Optional[EmailStr] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().replace(" ", "")
        if DIGITS_RE.match(v) or E164_RE.match(v) or (v.isdigit() and (len(v) == 12 and v.startswith("91"))):
            return v
        raise ValueError("phone must be 10 digits (India) or E.164 (e.g. +919876543210)")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 4 or len(v) > 10 or not v.isdigit():
            raise ValueError("code must be a numeric OTP")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("full_name is required")
        return v


class TokenPairResponse(BaseModel):
    token_type: str = "bearer"
    access_token: str
    refresh_token: str
    expires_in: int  # seconds
    user: UserResponse
    roles: List[str] = []


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
