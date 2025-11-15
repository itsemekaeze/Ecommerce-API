from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi import BackgroundTasks
from src.users.models import UserRequest
from src.entities.users import UserModel
from src.entities.business import BusinessModel
from src.email.service import send_verification_email
from src.auth.service import get_hashed_password
import secrets
from PIL import Image


async def user_registration(
    user: UserRequest, 
    background_tasks: BackgroundTasks, 
    db: Session
):
    existing_email = db.query(UserModel).filter(UserModel.email == user.email).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"User with email {user.email} already exists"
        )
    
    
    existing_username = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username {user.username} is already taken"
        )
    
    
    hashed_password = get_hashed_password(user.password)
    user_data = user.dict()
    user_data['password'] = hashed_password
    
    
    user_info = UserModel(**user_data)
    
    db.add(user_info)
    db.commit()
    db.refresh(user_info)
    
    
    business = BusinessModel(
        business_name=user_info.username,
        business_id=user_info.id
    )
    db.add(business)
    db.commit()
    db.refresh(business)
    
    
    await send_verification_email(user_info, background_tasks)
    
    return {
        "status": "ok",
        "data": f"Hello {user_info.username} Please check your email inbox for Account Verification"
    }


def user_details(db: Session, current_user: int):
    business = db.query(BusinessModel).filter(
        BusinessModel.business_id == current_user.id
    ).first()
    logo_url = "localhost:8000/static/images/" + business.logo
    return {
        "status": "ok",
        "data": {
            "username": current_user.username,
            "email": current_user.email,
            "verified": current_user.is_verified,
            "created_at": current_user.created_at,
            "logo": logo_url
        }
    }


async def upload_profile(db: Session, current_user: int, file: UploadFile = File(...)):
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

    business = db.query(BusinessModel).filter(
        BusinessModel.business_id == current_user.id
    ).first()

    owner = business.business_id

    if owner == current_user.id:
        business.logo = token_name

        db.commit()
        db.refresh(business)
    else:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authenticated to perform this action",
                headers={"WWW-Authenticate": "Bearer"}
                )
    file_url = "localhost:8000" + generate_file[1:]
    return {
        "status": "ok",
        "data": {
            "message": "Profile picture uploaded successfully",
            "file_path": generate_file,
            "file_url": file_url
        }
    }
   