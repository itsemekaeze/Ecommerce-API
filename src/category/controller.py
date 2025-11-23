from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.category.models import CategoryResponse, CategoryCreate
from src.category.service import create_category, list_category, delete_category, update_category
from src.entities.users import User
from src.users.models import UserRole
from src.auth.service import require_role, get_current_user
from src.database.core import get_db
from typing import List


router = APIRouter(
    tags=["Category"],
    prefix="/api/categories"
)



@router.post("/", response_model=CategoryResponse)
def create_categories(category: CategoryCreate, current_user: User = Depends(require_role(UserRole.SELLER)), 
                   db: Session = Depends(get_db)):
    data = create_category(category=category, current_user=current_user, db=db)

    return data

@router.get("/", response_model=List[CategoryResponse])
def list_categories(current_user: User = Depends(require_role(UserRole.SELLER)), db: Session = Depends(get_db)):
    data = list_category(current_user, db=db)

    return data


@router.put("/{category_id}", response_model=CategoryResponse)
def update_categories(category_id: int, category: CategoryCreate, 
                   current_user: User = Depends(require_role(UserRole.SELLER)), db: Session = Depends(get_db)):
    data = update_category(category_id, category, current_user, db)

    return data


@router.delete("/{category_id}")
def delete_categories(category_id: int, current_user: User = Depends(require_role(UserRole.SELLER)), 
                   db: Session = Depends(get_db)):
    data = delete_category(category_id, current_user, db)

    return data

