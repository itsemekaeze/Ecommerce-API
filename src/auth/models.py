from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from src.entities.users import UserRole
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        disposable_domains = [
            'tempmail.com', 'throwaway.email', '10minutemail.com', 
            'guerrillamail.com', 'mailinator.com', 'trashmail.com',
            'fakeinbox.com', 'yopmail.com', 'getnada.com'
        ]
        
        email_domain = v.split('@')[1].lower()
        if email_domain in disposable_domains:
            raise ValueError('Disposable email addresses are not allowed')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        
        return v.lower()
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 20:
            raise ValueError('Username must not exceed 20 characters')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        
        if v[0].isdigit():
            raise ValueError('Username cannot start with a number')
        
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        weak_passwords = [
            'password', 'password123', '12345678', 'qwerty123', 
            'abc123', 'password1', 'welcome123', 'admin123'
        ]
        if v.lower() in weak_passwords:
            raise ValueError('This password is too common')
        
        return v
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is None:
            return v
        
        v = ' '.join(v.split())
        
        if len(v) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        
        if len(v) > 100:
            raise ValueError('Full name must not exceed 100 characters')
        
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError('Full name can only contain letters, spaces, hyphens, apostrophes, and periods')
        
        return v
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

class Token(BaseModel):
    access_token: str
    token_type : str


class TokenData(BaseModel):
    id: Optional[str] = None


class EmailVerificationResponse(BaseModel):
    message: str
    email: str
    status: str