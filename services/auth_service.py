"""
Auth service: refresh tokens + helpers.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models import RefreshToken, User, Role


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def issue_refresh_token(
    db: Session,
    *,
    user: User,
    created_ip: Optional[str],
    user_agent: Optional[str],
) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = _sha256_hex(token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        created_ip=created_ip,
        user_agent=user_agent,
    )
    db.add(rt)
    db.commit()
    return token


def rotate_refresh_token(
    db: Session,
    *,
    refresh_token: str,
    created_ip: Optional[str],
    user_agent: Optional[str],
) -> Tuple[User, str]:
    token_hash = _sha256_hex(refresh_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if rt.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
    if rt.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = db.query(User).filter(User.id == rt.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # Rotate: revoke current, issue a new one
    new_token = secrets.token_urlsafe(48)
    new_hash = _sha256_hex(new_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        expires_at=expires_at,
        created_ip=created_ip,
        user_agent=user_agent,
    )
    db.add(new_rt)
    db.flush()  # get new_rt.id without commit

    rt.revoked_at = datetime.utcnow()
    rt.replaced_by_token_id = new_rt.id

    db.commit()
    return user, new_token


def revoke_refresh_token(db: Session, *, refresh_token: str) -> None:
    token_hash = _sha256_hex(refresh_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not rt:
        return
    if rt.revoked_at is None:
        rt.revoked_at = datetime.utcnow()
        db.commit()


def get_role_names(user: User) -> List[str]:
    return [r.role_name for r in (user.roles or [])]


def ensure_default_role(db: Session, user: User, *, role_name: str) -> None:
    role_name = role_name.strip().lower()
    role = db.query(Role).filter(Role.role_name == role_name).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Role configuration missing")
    if role not in (user.roles or []):
        user.roles.append(role)


ALLOWED_SIGNUP_ROLES = {"buyer", "retailer", "wholesaler"}


def pick_signup_role(requested_role: Optional[str]) -> str:
    """
    Decide which role to assign during self-signup.

    Prevent privilege escalation by allowing only a safe list of roles.
    """
    if not requested_role:
        return "buyer"
    r = requested_role.strip().lower()
    # Back-compat alias: treat "seller" as "retailer" (role name is retailer).
    if r == "seller":
        r = "retailer"
    if r not in ALLOWED_SIGNUP_ROLES:
        return "buyer"
    return r
