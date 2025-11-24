from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.entities.order import Order, OrderStatus
from src.entities.payments import Payment, PaymentStatus
from src.database.core import get_db
from src.payment.models import PaymentCreate
from src.entities.users import User, UserRole
import uuid
from src.auth.service import get_current_user, require_role


def process_payment(payment_data: PaymentCreate, current_user: User = Depends(require_role([UserRole.CUSTOMER,UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == payment_data.order_id, Order.customer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    existing_payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already processed")
    
    
    
    transaction_id = str(uuid.uuid4())
    
    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment_data.payment_method,
        payment_status=PaymentStatus.COMPLETED,
        transaction_id=transaction_id
    )
    db.add(payment)
    
    order.status = OrderStatus.PROCESSING
    db.commit()
    db.refresh(payment)
    return payment

def get_all_payment(current_user: User = Depends(require_role([UserRole.CUSTOMER, UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
   
    payments = db.query(Payment).all()
    
    return payments


def get_payment(payment_id: int, current_user: User = Depends(require_role([UserRole.CUSTOMER, UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return payment


def get_payment_by_order(order_id: int, current_user: User = Depends(require_role([UserRole.CUSTOMER, UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.customer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment