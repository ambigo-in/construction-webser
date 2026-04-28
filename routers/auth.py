"""
Authentication routes:
- Login/signup via mobile OTP (server-generated OTP + SMSCountry)
- Access JWT + rotating refresh tokens
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config import settings
from core.deps import get_client_ip, require_roles
from core.deps import get_current_user
from core.security import create_access_token
from database import get_db
from models import AuditLog, User
from schemas.auth_schemas import (
    LogoutRequest,
    OtpRequest,
    LoginOtpVerify,
    SignupOtpVerify,
    RefreshRequest,
    TokenPairResponse,
)
from schemas.user_schemas import UserResponse
from services.auth_service import (
    ensure_default_role,
    get_role_names,
    issue_refresh_token,
    pick_signup_role,
    rotate_refresh_token,
    revoke_refresh_token,
)
from services.smscountry_service import SMSCountryService, get_smscountry_service
from services.otp_service import create_otp, normalize_india_phone, otp_message, verify_otp
from utils.rate_limit import enforce_rate_limit


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin/ping")
def admin_ping(_: User = Depends(require_roles("admin"))):
    return {"status": "ok"}


@router.post("/otp/request")
async def request_otp(
    payload: OtpRequest,
    request: Request,
    db: Session = Depends(get_db),
    sms: SMSCountryService = Depends(get_smscountry_service),
):
    ip = get_client_ip(request)
    phone10 = normalize_india_phone(payload.phone)
    enforce_rate_limit(
        f"auth:otp:phone:{phone10}",
        limit=settings.AUTH_OTP_PER_PHONE_PER_HOUR,
        window_seconds=3600,
    )
    enforce_rate_limit(
        f"auth:otp:ip:{ip}",
        limit=settings.AUTH_OTP_PER_IP_PER_HOUR,
        window_seconds=3600,
    )

    otp = create_otp(
        db,
        phone10=phone10,
        created_ip=ip,
        user_agent=request.headers.get("user-agent"),
    )
    text = otp_message(otp)
    await sms.send_sms(number=phone10, content=text)

    existing_user = db.query(User).filter(User.phone == phone10).first()
    db.add(
        AuditLog(
            user_id=existing_user.id if existing_user else None,
            action="otp_requested",
            entity_type="user",
            entity_id=existing_user.id if existing_user else None,
            meta={"phone": phone10, "ip": ip},
        )
    )
    db.commit()

    return {"status": "sent", "is_registered": bool(existing_user)}


@router.post("/login/otp/verify", response_model=TokenPairResponse)
def login_with_otp_verify(
    payload: LoginOtpVerify,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = get_client_ip(request)
    phone10 = normalize_india_phone(payload.phone)
    enforce_rate_limit(
        f"auth:verify:phone:{phone10}",
        limit=settings.AUTH_VERIFY_PER_PHONE_PER_HOUR,
        window_seconds=3600,
    )

    user = db.query(User).filter(User.phone == phone10).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not registered")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    ok = verify_otp(db, phone10=phone10, otp=payload.code)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    if not user.is_verified:
        user.is_verified = True
        db.commit()
        db.refresh(user)

    roles = [r.lower() for r in get_role_names(user)]
    access_token, expires_in = create_access_token(user_id=str(user.id), roles=roles)
    refresh_token = issue_refresh_token(
        db,
        user=user,
        created_ip=ip,
        user_agent=request.headers.get("user-agent"),
    )

    db.add(
        AuditLog(
            user_id=user.id,
            action="login_otp",
            entity_type="user",
            entity_id=user.id,
            meta={"phone": user.phone, "ip": ip, "roles": roles},
        )
    )
    db.commit()

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user=user,
        roles=roles,
    )


@router.post("/signup/otp/verify", response_model=TokenPairResponse)
def signup_with_otp_verify(
    payload: SignupOtpVerify,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = get_client_ip(request)
    phone10 = normalize_india_phone(payload.phone)
    enforce_rate_limit(
        f"auth:verify:phone:{phone10}",
        limit=settings.AUTH_VERIFY_PER_PHONE_PER_HOUR,
        window_seconds=3600,
    )

    existing = db.query(User).filter(User.phone == phone10).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already registered")

    ok = verify_otp(db, phone10=phone10, otp=payload.code)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    user = User(
        full_name=payload.full_name.strip(),
        email=str(payload.email).strip().lower() if payload.email else None,
        phone=phone10,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.flush()

    role_name = pick_signup_role(payload.requested_role)
    ensure_default_role(db, user, role_name=role_name)

    db.commit()
    db.refresh(user)

    roles = [r.lower() for r in get_role_names(user)]
    access_token, expires_in = create_access_token(user_id=str(user.id), roles=roles)
    refresh_token = issue_refresh_token(
        db,
        user=user,
        created_ip=ip,
        user_agent=request.headers.get("user-agent"),
    )

    db.add(
        AuditLog(
            user_id=user.id,
            action="signup_otp",
            entity_type="user",
            entity_id=user.id,
            meta={"phone": user.phone, "ip": ip, "roles": roles},
        )
    )
    db.commit()

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        user=user,
        roles=roles,
    )


@router.post("/token/refresh", response_model=TokenPairResponse)
def refresh_tokens(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = get_client_ip(request)
    enforce_rate_limit(
        f"auth:refresh:ip:{ip}",
        limit=settings.AUTH_REFRESH_PER_IP_PER_MINUTE,
        window_seconds=60,
    )

    user, new_refresh_token = rotate_refresh_token(
        db,
        refresh_token=payload.refresh_token,
        created_ip=ip,
        user_agent=request.headers.get("user-agent"),
    )

    roles = [r.lower() for r in get_role_names(user)]
    access_token, expires_in = create_access_token(user_id=str(user.id), roles=roles)

    db.add(
        AuditLog(
            user_id=user.id,
            action="token_refreshed",
            entity_type="user",
            entity_id=user.id,
            meta={"ip": ip},
        )
    )
    db.commit()

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
        user=user,
        roles=roles,
    )


@router.post("/logout")
def logout(
    payload: LogoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    ip = get_client_ip(request)
    revoke_refresh_token(db, refresh_token=payload.refresh_token)
    db.add(
        AuditLog(
            user_id=None,
            action="logout",
            entity_type="auth",
            entity_id=None,
            meta={"ip": ip},
        )
    )
    db.commit()
    return {"status": "ok"}
