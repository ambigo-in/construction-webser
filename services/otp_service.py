"""
OTP generation + verification (server-side).
"""
from __future__ import annotations

import hmac
import secrets
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models import OtpCode


def normalize_india_phone(phone: str) -> str:
    """
    Normalize common representations to a 10-digit Indian mobile number.
    Accepts:
    - "7997931130"
    - "917997931130"
    - "+917997931130"
    """
    p = phone.strip().replace(" ", "")
    if p.startswith("+"):
        p = p[1:]
    if p.startswith(settings.SMS_DEFAULT_COUNTRY_CODE):
        p = p[len(settings.SMS_DEFAULT_COUNTRY_CODE):]
    if not p.isdigit() or len(p) != 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="phone must be a 10-digit number")
    return p


def generate_otp(*, length: int | None = None) -> str:
    n = length if length is not None else settings.OTP_LENGTH
    # Ensure first digit isn't always 0 by using range.
    lo = 10 ** (n - 1)
    hi = (10 ** n) - 1
    return str(secrets.randbelow(hi - lo + 1) + lo)


def otp_message(otp: str) -> str:
    # Must match your registered DLT template exactly (except variable replacement).
    return settings.SMS_OTP_TEMPLATE.format(otp=otp)


def _otp_digest(phone10: str, otp: str) -> str:
    """
    HMAC(phone:otp, SECRET_KEY) => hex digest
    """
    msg = f"{phone10}:{otp}".encode("utf-8")
    key = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(key, msg, sha256).hexdigest()


def create_otp(db: Session, *, phone10: str, created_ip: Optional[str], user_agent: Optional[str]) -> str:
    otp = generate_otp()
    digest = _otp_digest(phone10, otp)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    row = OtpCode(
        phone=phone10,
        purpose="login",
        code_hash=digest,
        expires_at=expires_at,
        created_ip=created_ip,
        user_agent=user_agent,
    )
    db.add(row)
    return otp


def verify_otp(db: Session, *, phone10: str, otp: str) -> bool:
    """
    Verify OTP against the latest unconsumed record within expiry window.
    """
    now = datetime.utcnow()
    row = (
        db.query(OtpCode)
        .filter(OtpCode.phone == phone10)
        .filter(OtpCode.purpose == "login")
        .filter(OtpCode.consumed_at.is_(None))
        .order_by(OtpCode.created_at.desc())
        .first()
    )
    if not row:
        return False
    if row.expires_at <= now:
        return False
    if row.attempts >= settings.OTP_MAX_VERIFY_ATTEMPTS:
        return False

    expected = row.code_hash
    got = _otp_digest(phone10, otp.strip())
    ok = hmac.compare_digest(expected, got)
    row.attempts = int(row.attempts or 0) + 1
    if ok:
        row.consumed_at = now
    db.commit()
    return ok
