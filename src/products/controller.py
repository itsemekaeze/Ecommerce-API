from fastapi import APIRouter, Depends, File, UploadFile
from src.products.models import ProductCreate, ProductUpdate
from src.products.service import add_new_product, get_all_products, get_individual_product, delete_product, uploadfile_product, update_product
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.auth.service import get_current_user

router = APIRouter(
    tags=["Products"],
    prefix="/products"
)


@router.post("/create")
async def create_products(data: ProductCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return await add_new_product(product=data, db=db, current_user=current_user)


@router.get("/")
def get_products(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return get_all_products(db=db, current_user=current_user)

@router.post("/upload/{id}")
async def upload_products_image(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user), file: UploadFile = File(...)):
    return await uploadfile_product(id=id, db=db, current_user=current_user, file=file)

@router.get("/{id}")
async def get_individual_products(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return await get_individual_product(id=id, db=db, current_user=current_user)


@router.delete("/{id}")
async def delete_products(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return await delete_product(id=id, db=db, current_user=current_user)


@router.put("/{id}")
async def update_products(id: int, product_update: ProductUpdate, db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    return await update_product(id, product_update, db, current_user)