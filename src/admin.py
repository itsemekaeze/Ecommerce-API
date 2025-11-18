from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.entities.users import User, UserRole
from src.entities.products import Product
from src.entities.order import Order, OrderStatus
from src.order.models import OrderResponse
from src.auth.service import require_role
from src.database.core import get_db
from typing import List


router = APIRouter(
    tags=["Admin Dashboard"],
    prefix="/api/admin"
)


@router.get("/stats")
def get_admin_stats(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(Order).filter(Order.status != OrderStatus.CANCELLED).with_entities(
        db.query(Order.total_amount).label('total')
    ).scalar() or 0
    
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders
    }

@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(current_user: User = Depends(require_role([UserRole.ADMIN])), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    
    return db.query(Order).offset(skip).limit(limit).all()
