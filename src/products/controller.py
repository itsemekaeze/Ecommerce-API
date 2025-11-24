from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from src.products.models import ProductResponse
from src.products.service import create_product, list_products, get_product, update_product, delete_product, get_product_review, upload_product_image
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from src.users.models import UserRole
from typing import List, Optional
from src.auth.service import require_role, get_current_user
from src.review.models import ReviewResponse

router = APIRouter(
    tags=["Products"],
    prefix="/api/products"
)

@router.post("/requested-role")
def become_seller(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Upgrade your account to SELLER status.
    
    - One-click to become a seller
    - This action is permanent (cannot revert to customer)
    - Sellers can create and manage products
    """
    
    # Check if user is already a seller
    if current_user.role == UserRole.SELLER:
        return {
            "message": "You are already a seller",
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role.value
        }
    
    # Check if user is admin (admins shouldn't downgrade)
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot change roles"
        )
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can become sellers"
        )
    
    # Upgrade customer to seller
    current_user.role = UserRole.SELLER
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Congratulations! You are now a seller!",
        "user_id": current_user.id,
        "username": current_user.username,
        "note": "You can now create and sell products"
    }

@router.post("/", response_model=ProductResponse)
async def create_products(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    data = create_product(name, description, price, stock, category_id, image, current_user, db)

    return await data


@router.get("/", response_model=List[ProductResponse])
def list_of_products(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    data = list_products(current_user, skip, limit, db)

    return data

@router.get("/{product_id}", response_model=ProductResponse)
def get_products(product_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):

    data = get_product(product_id, current_user, db)

    return data


@router.put("/{product_id}", response_model=ProductResponse)
async def update_products(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    
    data = update_product(product_id, name, description, price, stock, category_id, image, current_user, db)

    return await data


@router.delete("/{product_id}")
def delete_products(product_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), 
                  db: Session = Depends(get_db)):
    
    data = delete_product(product_id, current_user, db)

    return data


@router.post("/upload/product-image")
async def upload_product_images(file: UploadFile = File(...), current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    return await upload_product_image(file, current_user, db)


@router.get("/{product_id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(product_id: int, current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):
    data = get_product_review(product_id, current_user, db)
    return data

