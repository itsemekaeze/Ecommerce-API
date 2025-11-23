from pydantic import BaseModel, field_validator
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    category_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Product name cannot be empty')
        if len(v) < 3:
            raise ValueError('Product name must be at least 3 characters long')
        if len(v) > 200:
            raise ValueError('Product name must not exceed 200 characters')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError('Description must not exceed 2000 characters')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        if v > 1000000:
            raise ValueError('Price must not exceed 1,000,000')
        return round(v, 2)
    
    @field_validator('stock')
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock cannot be negative')
        if v > 1000000:
            raise ValueError('Stock must not exceed 1,000,000')
        return v

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    category_id: Optional[int] = None 
    seller_id: int
    is_active: bool
    
    class Config:
        from_attributes = True
        