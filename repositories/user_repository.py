"""User database operations."""
from uuid import UUID

from sqlalchemy.orm import Session

from models import User


def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def update_user(db: Session, user: User, data: dict):
    for key, value in data.items():
        setattr(user, key, value)
    db.flush()
    return user

