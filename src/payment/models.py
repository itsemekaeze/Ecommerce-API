from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.entities.payments import PaymentStatus

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    card_number: Optional[str] = None
    card_cvv: Optional[str] = None
    card_expiry: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    payment_status: PaymentStatus
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True