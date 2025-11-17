from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from src.users.models import UserRole
from src.entities.users import User
from src.auth.service import require_role, get_current_user
from src.database.core import get_db
from typing import Optional


def list_users(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    return db.query(User).all()



def update_user(user_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, 
                current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if full_name:
        user.full_name = full_name
    if phone:
        user.phone = phone
    
    db.commit()
    db.refresh(user)
    
    return user