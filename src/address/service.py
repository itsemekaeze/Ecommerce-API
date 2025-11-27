from src.address.models import AddressCreate
from src.auth.service import get_current_user, require_role
from sqlalchemy.orm import Session
from src.entities.users import User, UserRole
from fastapi import Depends
from src.database.core import get_db
from src.entities.shipping_address import Address


def create_address(address: AddressCreate, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.CUSTOMER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    
    db_address = Address(user_id=current_user.id, **address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


def list_addresses(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.CUSTOMER, UserRole.ADMIN])), db: Session = Depends(get_db)):
        
    return db.query(Address).filter(Address.user_id == current_user.id).all()
