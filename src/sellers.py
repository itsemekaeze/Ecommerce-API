from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.entities.users import User, UserRole
from src.entities.products import Product
from src.entities.order import Order, OrderStatus, OrderItem
from src.order.models import OrderResponse
from src.auth.service import require_role
from src.database.core import get_db
from typing import List
from src.products.models import ProductResponse

router = APIRouter(
    tags=["Seller Dashboard"],
    prefix="/api/seller"
)



@router.get("/stats")
def get_seller_stats(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    
    total_products = db.query(Product).filter(Product.seller_id == current_user.id).count()
    active_products = db.query(Product).filter(
        Product.seller_id == current_user.id,
        Product.is_active == True
    ).count()
    
    
    revenue = db.query(OrderItem).join(Product).join(Order).filter(
        Product.seller_id == current_user.id,
        Order.status != OrderStatus.CANCELLED
    ).with_entities(
        db.query(OrderItem.price * OrderItem.quantity).label('total')
    ).scalar() or 0
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "total_revenue": revenue
    }


@router.get("/products", response_model=List[ProductResponse])
def get_seller_products(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                       db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.seller_id == current_user.id).all()

@router.get("/orders", response_model=List[OrderResponse])
def get_seller_orders(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                     db: Session = Depends(get_db)):
    
    orders = db.query(Order).join(OrderItem).join(Product).filter(
        Product.seller_id == current_user.id
    ).distinct().all()

    return orders

