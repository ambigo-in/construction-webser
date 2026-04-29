"""Audit log database operations."""
from typing import Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from models import AuditLog


def create_audit_log(
    db: Session,
    *,
    user_id: Optional[UUID],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    meta: Optional[dict] = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        meta=jsonable_encoder(meta) if meta is not None else None,
    )
    db.add(log)
    return log


def list_audit_logs(db: Session, *, limit: int = 100):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
