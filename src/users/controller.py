from fastapi import APIRouter, UploadFile, File
from src.users.models import UserResponse
from src.entities.users import User, UserRole
from sqlalchemy.orm import Session
from fastapi import Depends
from src.database.core import get_db
from src.auth.service import require_role
from typing import List, Optional
from src.users.service import list_users, update_user, upload_profile_picture, user_profiles

router = APIRouter(
    tags=["Users"],
    prefix="/api/users"
)


@router.get("/", response_model=List[UserResponse])
def list_all_users(current_user: User = Depends(require_role([UserRole.ADMIN])), db: Session = Depends(get_db)):

    data = list_users(current_user, db)
    
    return data



@router.put("/{user_id}", response_model=UserResponse)
def update_users(user_id: int, full_name: Optional[str] = None, phone: Optional[str] = None, 
                current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN, UserRole.CUSTOMER])), db: Session = Depends(get_db)):
    data = update_user(user_id=user_id, full_name=full_name, phone=phone, current_user=current_user, db=db)

    return data


@router.get("/profile", response_model=UserResponse)
def users_profile(current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN, UserRole.CUSTOMER]))):

    return user_profiles(current_user)

@router.post("/upload/profile-picture")
async def upload_user_profile(file: UploadFile = File(...), current_user: User = Depends(require_role([UserRole.SELLER, UserRole.ADMIN, UserRole.CUSTOMER])), db: Session = Depends(get_db)):
    
    return await upload_profile_picture(file, current_user, db)