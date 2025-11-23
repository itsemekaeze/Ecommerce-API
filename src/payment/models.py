from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from src.entities.payments import PaymentStatus

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    card_number: Optional[str] = None
    card_cvv: Optional[str] = None
    card_expiry: Optional[str] = None

    @field_validator('order_id')
    @classmethod
    def validate_order_id(cls, v):
        if v <= 0:
            raise ValueError('Order ID must be a positive integer')
        return v
    
    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        allowed_methods = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
        if v.lower() not in allowed_methods:
            raise ValueError(f'Payment method must be one of: {", ".join(allowed_methods)}')
        return v.lower()
    
   

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