from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, UploadFile, File
from src.users.models import UserRole
from src.entities.users import User
from src.auth.service import require_role, get_current_user
from src.database.core import get_db
from typing import Optional
from pathlib import Path
import shutil
import uuid
import os
from src.auth.service import require_verified



UPLOAD_DIR = Path("static")
UPLOAD_DIR.mkdir(exist_ok=True)
PROFILE_IMAGES_DIR = UPLOAD_DIR / "profiles"
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


def list_users(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):
    return db.query(User).all()



def update_user(user_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, 
                current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if full_name:
        user.full_name = full_name
    if phone:
        user.phone = phone
    
    db.commit()
    db.refresh(user)
    
    return user


async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db)
):
    validate_image_file(file)
    
    
    if current_user.profile_picture and os.path.exists(current_user.profile_picture):
        os.remove(current_user.profile_picture)
    
    
    file_path = save_upload_file(file, PROFILE_IMAGES_DIR)
    
    
    current_user.profile_picture = file_path
    db.commit()
    db.refresh(current_user)
    
    return current_user