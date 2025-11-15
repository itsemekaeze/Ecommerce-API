from fastapi import APIRouter, Depends
from src.business.models import BusinessUpdate
from src.business.service import update_business_id, get_all_business
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.auth.service import get_current_user

router = APIRouter(
    tags=["Business"],
    prefix="/business"
)

@router.get("/")
def get_business(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return get_all_business(db=db, current_user=current_user)


@router.put("/{id}")
async def update_business(id: int, business_update: BusinessUpdate, db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    return await update_business_id(id, business_update, db, current_user)


