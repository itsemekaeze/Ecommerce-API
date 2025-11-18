from pydantic import BaseModel

class AddressCreate(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False

class AddressResponse(BaseModel):
    id: int
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    
    class Config:
        from_attributes = True