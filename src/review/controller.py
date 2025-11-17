from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.review.models import ReviewCreate, ReviewResponse
from src.entities.users import User
from src.auth.service import get_current_user
from src.review.service import create_review

router = APIRouter(
    tags=["Reviews"],
    prefix="/api/reviews"
)

@router.post("/", response_model=ReviewResponse)
def create_reviews(review: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    return create_review(review, current_user, db)
