from fastapi import APIRouter, Depends, File, UploadFile
from src.products.models import ProductCreate, ProductResponse
from src.products.service import create_product, list_products, get_product, update_product, delete_product, get_product_review
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from src.users.models import UserRole
from typing import List
from src.auth.service import require_role
from src.review.models import ReviewResponse

router = APIRouter(
    tags=["Products"],
    prefix="/api/products"
)


@router.post("/", response_model=ProductResponse)
def create_products(product: ProductCreate, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    data = create_product(product, current_user, db)

    return data


@router.get("/", response_model=List[ProductResponse])
def list_of_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    data = list_products(skip, limit, db)

    return data

@router.get("/{product_id}", response_model=ProductResponse)
def get_products(product_id: int, db: Session = Depends(get_db)):

    data = get_product(product_id, db)

    return data


@router.put("/{product_id}", response_model=ProductResponse)
def update_products(product_id: int, product: ProductCreate, 
                  current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    
    data = update_product(product_id, product, current_user, db)

    return data


@router.delete("/{product_id}")
def delete_products(product_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    
    data = delete_product(product_id, current_user, db)

    return data

@router.get("/{product_id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    data = get_product_review(product_id, db)
    return data