from fastapi import APIRouter, Depends, File, UploadFile
from src.cart_items.models import CartItemResponse, CartItemCreate
from src.cart_items.service import add_to_cart, get_cart, update_cart_item, remove_from_cart
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from src.users.models import UserRole
from typing import List
from src.auth.service import get_current_user

router = APIRouter(
    tags=["Carts"],
    prefix="/api/cart"
)


@router.post("/", response_model=CartItemResponse)
def add_to_carts(item: CartItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
 
    return add_to_cart(item, current_user, db)

@router.get("/", response_model=List[CartItemResponse])
def get_all_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    return get_cart(current_user, db)

@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_items(item_id: int, quantity: int, current_user: User = Depends(get_current_user), 
                    db: Session = Depends(get_db)):
    
    return update_cart_item(item_id, quantity, current_user, db)


@router.delete("/{item_id}")
def remove_from_carts(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    return remove_from_cart(item_id, current_user, db)