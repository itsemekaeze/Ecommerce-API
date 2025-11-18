from sqlalchemy.orm import Session
from src.cart_items.models import CartItemCreate
from src.entities.carts import CartItem
from src.entities.users import User
from src.entities.products import Product
from fastapi import HTTPException, Depends, Response, status
from src.auth.service import get_current_user
from src.database.core import get_db

def add_to_cart(item: CartItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    cart_item = CartItem(user_id=current_user.id, **item.dict())
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(CartItem).filter(CartItem.user_id == current_user.id).all()



def update_cart_item(item_id: int, quantity: int, current_user: User = Depends(get_current_user), 
                    db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)