"""
Security utilities: password hashing + JWT access tokens.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext

from config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(*, user_id: str, roles: List[str], expires_minutes: int | None = None) -> Tuple[str, int]:
    """
    Create a signed JWT access token.

    JWT is signed (not encrypted). Keep only non-sensitive data in claims.
    """
    expire_minutes = expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire_dt = datetime.utcnow() + timedelta(minutes=expire_minutes)
    expires_in = int((expire_dt - datetime.utcnow()).total_seconds())

    to_encode: Dict[str, Any] = {
        "sub": user_id,
        "roles": roles,
        "typ": "access",
        "jti": str(uuid.uuid4()),
        "iat": int(datetime.utcnow().timestamp()),
        "exp": expire_dt,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expires_in


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("typ") != "access":
        raise JWTError("Invalid token type")
    return payload

