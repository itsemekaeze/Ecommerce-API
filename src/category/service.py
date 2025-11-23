from src.category.models import CategoryCreate
from src.entities.users import User
from src.entities.category import Category
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.auth.service import require_role, get_current_user
from src.users.models import UserRole


def create_category(category: CategoryCreate, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                   db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


def list_category(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    return db.query(Category).all()


def update_category(category_id: int, category: CategoryCreate, 
                   current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_category.name = category.name
    db_category.description = category.description
    db.commit()
    db.refresh(db_category)

    return db_category



def delete_category(category_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                   db: Session = Depends(get_db)):
    
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)