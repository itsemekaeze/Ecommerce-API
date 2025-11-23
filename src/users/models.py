from pydantic import BaseModel, EmailStr
from typing import Optional
from src.entities.users import UserRole

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    # role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True