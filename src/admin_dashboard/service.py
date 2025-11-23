from fastapi import Depends
from sqlalchemy.orm import Session
from src.entities.products import Product
from src.entities.order import Order, OrderStatus
from fastapi import Depends, HTTPException, Response
from src.entities.users import User, UserRole
from src.database.core import get_db
from typing import Optional
from src.auth.service import require_role
from sqlalchemy import func


def get_dashboard_overview(current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
        
    total_users = db.query(User).count()
    total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.status != OrderStatus.CANCELLED)
        .scalar()
    ) or 0
    
    
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    processing_orders = db.query(Order).filter(Order.status == OrderStatus.PROCESSING).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count()
    
    
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    
    
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    
    
    low_stock_products = db.query(Product).filter(Product.stock < 10).all()
    
    
    alerts = []
    if pending_orders > 0:
        alerts.append({
            "type": "warning",
            "message": f"{pending_orders} orders pending review"
        })
    if len(low_stock_products) > 0:
        alerts.append({
            "type": "info",
            "message": f"{len(low_stock_products)} products with low stock"
        })
    
    
    return {
        "stats": {
            "total_users": total_users,
            "total_sellers": total_sellers,
            "total_customers": total_customers,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "pending_orders": pending_orders
        },
        "orders_by_status": {
            "pending": pending_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders,
            "cancelled": cancelled_orders
        },
        "recent_orders": [
            {
                "id": order.id,
                "customer_id": order.customer_id,
                "total_amount": order.total_amount,
                "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
                "created_at": str(order.created_at)
            } 
            for order in recent_orders
        ],
        "recent_users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "is_verified": user.is_verified,
                "created_at": str(user.created_at)
            } 
            for user in recent_users
        ],
        "low_stock_products": [
            {
                "id": product.id,
                "name": product.name,
                "stock": product.stock,
                "price": product.price
            }
            for product in low_stock_products
        ],
        "alerts": alerts
    }



def get_admin_stat(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):

    total_users = db.query(User).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    
    total_revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.status != OrderStatus.CANCELLED)
        .scalar()
    ) or 0
    
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    
    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "pending_orders": pending_orders
    }


def get_all_order(current_user: User = Depends(require_role([UserRole.ADMIN])), status: Optional[str] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    
    query = db.query(Order)
    
    if status:
        try:
            order_status = OrderStatus(status.lower())
            query = query.filter(Order.status == order_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()



def list_user(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    user = db.query(User).all()
    return user


def get_individual_users(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])), 
    db: Session = Depends(get_db)
):
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    return user

def delete_user(user_id: int, current_user: User = Depends(require_role([UserRole.ADMIN])), 
    db: Session = Depends(get_db)
):
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    

    user = db.query(User).filter(User.id == user_id)
    user_query = user.first()
    if user_query == None:
        raise HTTPException(status_code=404, detail="user not found")
    
    user.delete(synchronize_session=False)

    db.commit()
    
    return Response(status_code=204)

