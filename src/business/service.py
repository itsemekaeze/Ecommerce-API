from sqlalchemy.orm import Session
from src.business.models import BusinessUpdate
from src.entities.business import BusinessModel
from fastapi import HTTPException, status


def get_all_business(db: Session, current_user: int):
    business = db.query(BusinessModel).all()

    return {
        "status": "ok",
        "data": business
    }

async def update_business_id(id: int, business_update: BusinessUpdate, db: Session, current_user):
    business = db.query(BusinessModel).filter(
        BusinessModel.business_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    if business.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this business"
        )
    
    update_data = business_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    
    response_data = {
        "id": business.id,
        "business_name": business.business_name,
        "city": business.city,
        "region": business.region,
        "business_description": business.business_description,
        "logo": business.logo,
    }
    
    return {
        "status": "ok",
        "data": response_data
    }