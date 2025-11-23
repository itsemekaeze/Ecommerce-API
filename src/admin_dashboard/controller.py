from sqlalchemy.orm import Session
from src.order.models import OrderResponse
from src.users.models import UserResponse
from fastapi import APIRouter, Depends, Query
from src.entities.users import User, UserRole
from src.database.core import get_db
from src.auth.service import require_role
from typing import List, Optional
from src.admin_dashboard.service import (get_admin_stat, get_all_order, list_user, get_individual_users, delete_user, get_dashboard_overview)

router = APIRouter(
    tags=["Admin Dashboard"],
    prefix="/api/admin"
)


@router.get("/dashboard")
def admin_dashboard(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    
    return get_dashboard_overview(current_user, db)


@router.get("/stats")
def get_statistics(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    
    return get_admin_stat(current_user, db)


@router.get("/orders", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(require_role([UserRole.ADMIN])), 
    status: Optional[str] = Query(None, description="Filter by status: pending, processing, shipped, delivered, cancelled"),
    skip: int = 0, 
    limit: int = 50,
    db: Session = Depends(get_db)
):
    
    return get_all_order(current_user, status, skip, limit, db)


@router.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    
    return list_user(current_user, db)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])), 
    db: Session = Depends(get_db)
):
    
    return get_individual_users(user_id, current_user, db)

@router.delete("/users/{user_id}")
def remove_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])), 
    db: Session = Depends(get_db)
):
    
        
    return delete_user(user_id, current_user, db)
