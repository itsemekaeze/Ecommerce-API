from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import UserModel
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.service import verify_password, create_access_token
from src.auth.models import Token


router = APIRouter(
    tags=["Authentication"],
    prefix="/auth"
)


@router.post("/token", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    access_token = create_access_token(data={"id": user.id})

        
    return {"access_token": access_token, "token_type": "bearer"}
