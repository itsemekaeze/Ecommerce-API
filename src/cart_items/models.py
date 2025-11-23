from src.products.models import ProductResponse
from pydantic import BaseModel, field_validator


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

    @field_validator('product_id')
    @classmethod
    def validate_product_id(cls, v):
        if v <= 0:
            raise ValueError('Product ID must be a positive integer')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 1000:
            raise ValueError('Quantity cannot exceed 1000 items')
        return v

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    class Config:
        from_attributes = True