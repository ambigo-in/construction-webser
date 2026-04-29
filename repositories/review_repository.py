"""Review database operations."""
from sqlalchemy.orm import Session

from models import Review


def create_review(db: Session, data: dict):
    review = Review(**data)
    db.add(review)
    db.flush()
    return review


def get_review_for_order(db: Session, order_id):
    return db.query(Review).filter(Review.order_id == order_id).first()

