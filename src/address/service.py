from src.address.models import AddressCreate
from src.auth.service import get_current_user
from sqlalchemy.orm import Session
from src.entities.users import User, UserRole
from fastapi import Depends, HTTPException, status
from src.database.core import get_db
from src.entities.shipping_address import Address


def create_address(address: AddressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    db_address = Address(user_id=current_user.id, **address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


def list_addresses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    
    return db.query(Address).filter(Address.user_id == current_user.id).all()
