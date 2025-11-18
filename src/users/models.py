from pydantic import BaseModel, EmailStr
from typing import Optional
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SELLER = "seller"
    CUSTOMER = "customer"

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True