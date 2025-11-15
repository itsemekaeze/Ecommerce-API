from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_verified: bool= False
    created_at: datetime = datetime.utcnow()
    
    class Config:
        from_attributes = True

class UserRequest(BaseModel):
    username: str
    email: str
    password: str
    

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True



