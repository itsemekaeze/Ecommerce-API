from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.entities.order import Order, OrderItem
from src.entities.reviews import Review
from src.database.core import get_db
from src.review.models import ReviewCreate
from src.entities.products import Product
from src.auth.service import get_current_user
from src.entities.users import User, UserRole



def create_review(review: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    
    has_purchased = db.query(OrderItem).join(Order).filter(
        Order.customer_id == current_user.id,
        OrderItem.product_id == review.product_id
    ).first()
    
    if not has_purchased:
        raise HTTPException(status_code=400, detail="You can only review products you've purchased")
    
    
    existing_review = db.query(Review).filter(
        Review.product_id == review.product_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(status_code=400, detail="You've already reviewed this product")
    
    db_review = Review(user_id=current_user.id, **review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
