from sqlalchemy.orm import Session
from src.products.models import ProductCreate, ProductUpdate
from src.entities.products import ProductModel
from src.entities.users import UserModel
from datetime import datetime
from fastapi import HTTPException, status, Response, File, UploadFile
from src.entities.business import BusinessModel
import secrets
from PIL import Image
from decimal import Decimal


async def add_new_product(product: ProductCreate, db: Session, current_user: int):

    business = db.query(BusinessModel).filter(
        BusinessModel.business_id == current_user.id
    ).first()

    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You do not have a business profile"
        )
    
    if business.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    data = product.dict()

    if data["original_price"] > 0:
        data["percentage_discount"] = (
            (data["original_price"] - data["new_price"])
            / data["original_price"]
        ) * 100

        new_product = ProductModel(
            name=data["name"],
            categories=data["categories"],
            description=data["description"],
            original_price=data["original_price"],
            new_price=data["new_price"],
            percentage_discount=data["percentage_discount"],
            offer_expiration_date=datetime.utcnow(),
            profile_id=business.id
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "status": "ok",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "categories": new_product.categories,
                "description": new_product.description,
                "original_price": new_product.original_price,
                "new_price": new_product.new_price,
                "percentage_discount": new_product.percentage_discount,
                "business_id": new_product.profile_id
            }
        }
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price must be grater than 0")


def get_all_products(db: Session, current_user: int):
    products = db.query(ProductModel).all()
    return products


async def get_individual_product(id: int, db: Session, current_user: int):

    products = db.query(ProductModel).filter(ProductModel.id == id).first()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Products with an id {id} does not exit")
    
    business = products.business

    owner = db.query(UserModel).filter(UserModel.id == business.business_id).first()

    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Owner does not exit")
    
    
 
    return {
        "status": "ok",
        "data": {
            "products_details": products,
            "business_details": {
                "name": business.business_name,
                "city": business.city,
                "region": business.region,
                "description": business.business_description,
                "logo": business.logo,
                "owner_id": owner.id,
                "email": owner.email,
                "created_at": datetime.utcnow()
            }
        }
    }



async def delete_product(id: int, db: Session, current_user: int):

    products = db.query(ProductModel).filter(ProductModel.id == id)

    products_query = products.first()

    if products_query == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Products with an id {id} does not exit")
    
    if products_query.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")

    products.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def uploadfile_product(id: int, db: Session, current_user: int, file: UploadFile = File(...)):
    FILEPATH = "./static/images/"

    if not file.filename or "." not in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    
    extension = file.filename.rsplit(".", 1)[-1].lower()
    
    
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension"
        )
    
    token_name = secrets.token_hex(10)+"."+extension

    generate_file = FILEPATH + token_name

    file_content = await file.read()

    with open(generate_file, "wb") as file:
        file.write(file_content)


    img = Image.open(generate_file)
    img = img.resize(size=(200, 200))

    img.save(generate_file)


    products = db.query(ProductModel).filter(ProductModel.id == id).first()

    business = products.business

    owner = db.query(UserModel).filter(UserModel.id == business.id).first()

    if owner.id == current_user.id:
        products.product_image = token_name

        db.commit()

    else:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated to perform this action",
                headers={"WWW-Authenticate": "Bearer"}
                )

    return {
        "status": "ok",
        "data": {
            "message": "Product picture uploaded successfully",
            "product_image": token_name
        }
    }


async def update_product(id: int, product_update: ProductUpdate, db: Session, current_user: int):
    products = db.query(BusinessModel).filter(
        BusinessModel.business_id == current_user.id
    ).first()
    
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    product = db.query(ProductModel).filter(ProductModel.id == id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.profile_id != products.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated to perform this action"
        )
    
    update_data = product_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    for field, value in update_data.items():
        if field != "new_price":  
            setattr(product, field, value)
    
    if "new_price" in update_data:
        new_price = Decimal(str(update_data["new_price"]))
        product.new_price = new_price
        
        if product.original_price and product.original_price > 0:
            original = Decimal(str(product.original_price))
            percentage_discount = ((original - new_price) / original) * 100
            product.percentage_discount = int(round(percentage_discount))
    
    product.offer_expiration_date = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    response_data = {
        "id": product.id,
        "name": product.name,
        "categories": product.categories,
        "description": product.description,
        "original_price": float(product.original_price) if product.original_price else None,
        "new_price": float(product.new_price) if product.new_price else None,
        "percentage_discount": product.percentage_discount,
        "offer_expiration_date": product.offer_expiration_date,
        "product_image": product.product_image,
        "date_published": datetime.utcnow(),
    }

    return {
        "status": "ok",
        "data": response_data
    }