from sqlalchemy.orm import Session
from src.users.models import UserRole
from src.entities.products import Product
from src.entities.users import User
from fastapi import HTTPException, status, Response, Depends, UploadFile, File, Form
from src.auth.service import require_role
from src.database.core import get_db
from src.entities.reviews import Review
import uuid
import shutil
from typing import Optional
from pathlib import Path
import os


UPLOAD_DIR = Path("static")
UPLOAD_DIR.mkdir(exist_ok=True)
PRODUCT_IMAGES_DIR = UPLOAD_DIR / "products"
PROFILE_IMAGES_DIR = UPLOAD_DIR / "profiles"
PRODUCT_IMAGES_DIR.mkdir(exist_ok=True)
PROFILE_IMAGES_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024 


def validate_image_file(file: UploadFile) -> None:
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )

def save_upload_file(file: UploadFile, directory: Path) -> str:
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = directory / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)


async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    image_url = None
    if image:
        validate_image_file(image)
        image_url = save_upload_file(image, PRODUCT_IMAGES_DIR)
    
    db_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        seller_id=current_user.id,
        image_url=image_url
    )
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



async def update_product(
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
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user.role != UserRole.ADMIN and db_product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if name:
        db_product.name = name
    if description:
        db_product.description = description
    if price:
        db_product.price = price
    if stock is not None:
        db_product.stock = stock
    if category_id:
        db_product.category_id = category_id
    if image:
        validate_image_file(image)

        if db_product.image_url and os.path.exists(db_product.image_url):
            os.remove(db_product.image_url)
        db_product.image_url = save_upload_file(image, PRODUCT_IMAGES_DIR)
    
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


async def upload_product_image(file: UploadFile = File(...), current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN])), db: Session = Depends(get_db)):

    validate_image_file(file)
    
    
    file_path = save_upload_file(file, PRODUCT_IMAGES_DIR)
    
    return {
        "message": "Product image uploaded successfully",
        "file_path": file_path,
        "file_url": f"/uploads/products/{Path(file_path).name}"
    }