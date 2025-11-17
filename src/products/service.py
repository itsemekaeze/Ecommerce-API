from sqlalchemy.orm import Session
from src.products.models import ProductCreate
from src.users.models import UserRole
from src.entities.products import Product
from src.entities.users import User
from datetime import datetime
from fastapi import HTTPException, status, Response, Depends
from src.auth.service import require_role
from src.database.core import get_db
from src.entities.reviews import Review


def create_product(product: ProductCreate, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    db_product = Product(**product.dict(), seller_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


def list_products(skip: int, limit: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()


def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



def update_product(product_id: int, product: ProductCreate, 
                  current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user.role != UserRole.ADMIN and db_product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(product_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user.role != UserRole.ADMIN and db_product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_product.is_active = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_product_review(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == product_id).all()