from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    categories: str
    description: str
    original_price: float
    new_price: float
    offer_expiration_date: datetime = datetime.utcnow()

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    categories: Optional[str] = None
    new_price: Optional[float] = None
    description: Optional[str] = None

