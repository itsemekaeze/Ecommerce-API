from fastapi import APIRouter, Depends
from src.address.models import AddressResponse, AddressCreate
from src.auth.service import get_current_user
from src.database.core import get_db
from sqlalchemy.orm import Session
from src.entities.users import User
from typing import List
from src.address.service import create_address, list_addresses

router = APIRouter(
    tags=["Shipping Address"],
    prefix="/api/addresses"
)


@router.post("/", response_model=AddressResponse)
def create_new_address(address: AddressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    return create_address(address, current_user, db)

@router.get("/", response_model=List[AddressResponse])
def list_all_address(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_addresses(current_user, db)