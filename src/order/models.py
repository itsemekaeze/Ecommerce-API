from pydantic import BaseModel
from datetime import datetime
from typing import List
from src.entities.order import OrderStatus
class OrderCreate(BaseModel):
    shipping_address_id: int

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
