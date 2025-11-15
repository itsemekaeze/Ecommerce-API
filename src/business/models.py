from pydantic import BaseModel
from typing import Optional


class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    business_description: Optional[str] = None


