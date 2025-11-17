from fastapi import APIRouter, Depends, File, UploadFile, Form
from src.products.models import ProductCreate, ProductResponse
from src.products.service import create_product, list_products, get_product, update_product, delete_product, get_product_review, upload_product_image
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from src.users.models import UserRole
from typing import List, Optional
from src.auth.service import require_role
from src.review.models import ReviewResponse

router = APIRouter(
    tags=["Products"],
    prefix="/api/products"
)


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
def list_of_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    data = list_products(skip, limit, db)

    return data

@router.get("/{product_id}", response_model=ProductResponse)
def get_products(product_id: int, db: Session = Depends(get_db)):

    data = get_product(product_id, db)

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
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    data = get_product_review(product_id, db)
    return data
