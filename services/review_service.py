"""Review business logic."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User
from repositories import audit_repository, order_repository, review_repository
from schemas.transaction_schemas import ReviewCreate


def create_review(db: Session, user: User, payload: ReviewCreate):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rating must be between 1 and 5")
    order = order_repository.get_order(db, payload.order_id)
    if not order or order.buyer_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.order_status != "delivered":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review can be added after delivery")
    if review_repository.get_review_for_order(db, order.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Review already exists for this order")
    review = review_repository.create_review(
        db,
        {
            "order_id": order.id,
            "buyer_id": user.id,
            "seller_id": order.seller_id,
            "rating": payload.rating,
            "review_text": payload.review_text,
        },
    )
    audit_repository.create_audit_log(db, user_id=user.id, action="review_created", entity_type="review", entity_id=review.id)
    db.commit()
    db.refresh(review)
    return review

