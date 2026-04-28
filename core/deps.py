"""
FastAPI dependencies for authentication + RBAC.
"""
from typing import Callable, List

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from database import get_db
from models import User
from core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # x-forwarded-for may be a comma-separated list
        return xff.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_uuid = UUID(str(user_id))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return user


def require_roles(*required_roles: str) -> Callable[[User], User]:
    required = {r.strip().lower() for r in required_roles if r and r.strip()}

    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if not required:
            return current_user
        user_roles: List[str] = [r.role_name.lower() for r in (current_user.roles or [])]
        if not any(r in required for r in user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return _dep
