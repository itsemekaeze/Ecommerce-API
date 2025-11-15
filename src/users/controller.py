from fastapi import APIRouter, File, UploadFile
from src.users.models import UserRequest
from src.users.service import user_registration, user_details, upload_profile
from sqlalchemy.orm import Session
from fastapi import Depends, BackgroundTasks
from src.database.core import get_db
from src.auth.service import get_current_user

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)



@router.post("/registeration", status_code=201)
async def register_user(
    user: UserRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    return await user_registration(user, background_tasks, db)


@router.get("/me")
def user_info(db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    return user_details(db, current_user=current_user)


@router.post("/upload/profile")
async def user_profile(db: Session = Depends(get_db), current_user: int = Depends(get_current_user), file: UploadFile = File(...)):
    return await upload_profile(db, current_user=current_user, file=file)