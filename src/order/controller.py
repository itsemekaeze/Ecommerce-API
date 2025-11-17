from fastapi import APIRouter, Depends
from src.order.models import OrderResponse, OrderCreate, OrderStatusUpdate
from src.auth.service import get_current_user
from src.database.core import get_db
from sqlalchemy.orm import Session
from src.entities.users import User
from src.users.service import require_role
from src.users.models import UserRole
from typing import List
from src.order.service import create_order, update_order_status, list_orders, get_order

router = APIRouter(
    tags=["Orders"],
    prefix="/api/orders"
)


@router.post("/", response_model=OrderResponse)
def create_orders(order_data: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    return create_order(order_data, current_user, db)

@router.get("/", response_model=List[OrderResponse])
def list_all_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_orders(current_user, db)


@router.get("/{order_id}", response_model=OrderResponse)
def get_individual_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_order(order_id, current_user, db)


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_orders_status(order_id: int, status_update: OrderStatusUpdate, 
                       current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                       db: Session = Depends(get_db)):
    return update_order_status(order_id, current_user, db)