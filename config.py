"""
Database configuration settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=True,
        extra="ignore",  # don't crash if .env has unrelated keys
    )
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/construction_marketplace_db"
    DATABASE_ECHO: bool = False  # Set to True for SQL logging
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # SMSCountry (OTP) - if set, we will use SMSCountry flow (server-generated OTP)
    SMS_COUNTRY_KEY: Optional[str] = None
    SMS_COUNTRY_TOKEN: Optional[str] = None
    SMS_SENDER_ID: str = "AMBHPL"
    SMS_DEFAULT_COUNTRY_CODE: str = "91"  # India
    # If your SMSCountry/India DLT setup requires a template id, set it here.
    SMS_DLT_TEMPLATE_ID: Optional[str] = None
    # OTP message must match the registered DLT template exactly (except variables).
    # Use "{otp}" placeholder for substitution.
    SMS_OTP_TEMPLATE: str = "Your Ambigo verification code is: {otp}. Please do not share it with anyone else."

    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_VERIFY_ATTEMPTS: int = 5

    # Rate limiting (in-memory, per process)
    AUTH_OTP_PER_PHONE_PER_HOUR: int = 5
    AUTH_OTP_PER_IP_PER_HOUR: int = 20
    AUTH_VERIFY_PER_PHONE_PER_HOUR: int = 10
    AUTH_REFRESH_PER_IP_PER_MINUTE: int = 30

    # API
    API_TITLE: str = "Construction Materials Marketplace API"
    API_VERSION: str = "1.0.0"

    # Environment
    ENVIRONMENT: str = "development"

    # Payment Gateway (optional)
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None


settings = Settings()
