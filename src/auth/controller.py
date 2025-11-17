from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.service import verify_password, create_access_token, get_hashed_password, get_current_user
from src.auth.models import UserLogin, Token, UserCreate, UserResponse


router = APIRouter(
    tags=["Authentication"],
    prefix="/api/auth"
)


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_hashed_password(user.password),
        full_name=user.full_name,
        phone=user.phone,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# @router.post("/login", response_model=Token)
# async def login_user(
#     form_data: UserLogin,
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.username == form_data.username).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
#     if not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    
#     access_token = create_access_token(data={"id": user.id, "role": user.role})

        
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = create_access_token(
        data={"id": user.id, "role": user.role}
    )

    return {"access_token": access_token,
    "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):

    return current_user


