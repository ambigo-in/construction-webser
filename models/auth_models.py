"""
Authentication-related models (refresh tokens, OTP codes).
"""
from sqlalchemy import Column, DateTime, ForeignKey, String, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from database import Base


class RefreshToken(Base):
    """
    Persisted refresh tokens (opaque tokens stored as hashes).

    We store only a SHA-256 hash of the token to reduce impact if the DB leaks.
    """
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    token_hash = Column(String(64), nullable=False, unique=True, index=True)  # sha256 hex

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)

    revoked_at = Column(DateTime, nullable=True, index=True)
    replaced_by_token_id = Column(UUID(as_uuid=True), nullable=True)

    created_ip = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")


Index("ix_refresh_tokens_user_expires", RefreshToken.user_id, RefreshToken.expires_at)


class OtpCode(Base):
    """
    Server-generated OTPs for phone verification/login.

    OTPs are stored as hashes (never in plain text).
    """
    __tablename__ = "otp_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    phone = Column(String(20), nullable=False, index=True)
    purpose = Column(String(50), nullable=False, default="login")

    code_hash = Column(String(64), nullable=False)  # sha256 hex / hmac digest
    attempts = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    consumed_at = Column(DateTime, nullable=True, index=True)

    created_ip = Column(String(64), nullable=True)
    user_agent = Column(String(255), nullable=True)


Index("ix_otp_codes_phone_expires", OtpCode.phone, OtpCode.expires_at)
