from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile, status
from src.users.models import UserRole
from src.entities.users import User
from src.auth.service import get_current_user, require_role
from src.database.core import get_db
from typing import Optional
import os
from src.upload_settings import validate_image_file, save_upload_file, PROFILE_IMAGES_DIR
from src.entities.images import Image
from ..cloudinary_config import cloudinary
import cloudinary.uploader


def list_users(current_user: User = Depends(require_role(UserRole.ADMIN)), db: Session = Depends(get_db)):
    return db.query(User).all()



def update_user(user_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, 
                current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Permission")
    if full_name:
        user.full_name = full_name
    if phone:
        user.phone = phone
    
    db.commit()
    db.refresh(user)
    
    return user


def get_profiles(current_user: User = Depends(get_current_user)):
    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Permission")
    return current_user

async def upload_profile_picture(file: UploadFile, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    if UserRole.CUSTOMER != current_user.role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Permission")
    
    validate_image_file(file)

    
    saved_path = save_upload_file(file, PROFILE_IMAGES_DIR)

    
    upload_result = cloudinary.uploader.upload(saved_path)

    
    image_url = upload_result.get("secure_url")
    public_id = upload_result.get("public_id")

    
    image_record = Image(url=image_url, public_id=public_id)
    db.add(image_record)
    db.commit()
    db.refresh(image_record)

    return {
        "message": "Upload successful",
        "image_url": image_url,
        "public_id": public_id,
        "id": image_record.id
    }
    