from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.payment.models import PaymentCreate, PaymentResponse
from src.entities.users import User, UserRole
from src.auth.service import get_current_user, require_role
from typing import List
from src.payment.service import process_payment, get_payment, get_payment_by_order, get_all_payment

router = APIRouter(
    tags=["Payment"],
    prefix="/api/payments"
)


@router.get("/", response_model=List[PaymentResponse])
def get_all_payments(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    return get_all_payment(current_user, db)

@router.post("/process", response_model=PaymentResponse)
def process_payments(payment_data: PaymentCreate, current_user: User = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
   
    return process_payment(payment_data, current_user, db)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_individuals_payment(payment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        
    return get_payment(payment_id, current_user, db)

@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_orders(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
       
    return get_payment_by_order(order_id, current_user, db)