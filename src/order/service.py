from src.order.models import OrderCreate, OrderStatusUpdate
from src.auth.service import get_current_user
from sqlalchemy.orm import Session
from src.entities.users import User
from fastapi import Depends, HTTPException, status
from src.database.core import get_db
from src.entities.order import Order, OrderItem, OrderStatus
from src.entities.carts import CartItem
from src.users.models import UserRole
from datetime import datetime
from src.auth.service import require_role



def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

  
    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == current_user.id,
            CartItem.id.in_(order_data.cart_item_ids)
        )
        .all()
    )

    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="No valid cart items selected for order")

    
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Product '{item.product.name}' does not have enough stock"
            )

    
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    
    order = Order(
        customer_id=current_user.id,
        total_amount=total_amount,
        shipping_address_id=order_data.shipping_address_id,
        status=OrderStatus.PENDING
    )
    db.add(order)
    db.flush()  

    
    for cart_item in cart_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.add(order_item)

        
        cart_item.product.stock -= cart_item.quantity

        
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    return order


def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.customer_id == current_user.id).all()
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    return order



def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.customer_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.CUSTOMER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insufficient Permission")
    
    return order


def update_order_status(order_id: int, status_update: OrderStatusUpdate, 
                       current_user: User = Depends(require_role(UserRole.ADMIN)), 
                       db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    
    return order