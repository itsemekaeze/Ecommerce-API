from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List
from src.entities.order import OrderStatus
class OrderCreate(BaseModel):
    shipping_address_id: int
    cart_item_ids: List[int] 


    @field_validator('shipping_address_id')
    @classmethod
    def validate_shipping_address(cls, v):
        if v <= 0:
            raise ValueError('Shipping address ID must be a positive integer')
        return v

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    status: OrderStatus
    shipping_address_id: int
    created_at: datetime
    order_items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
