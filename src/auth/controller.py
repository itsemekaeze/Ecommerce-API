from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.service import verify_password, create_access_token, get_hashed_password, get_current_user
from src.auth.models import Token, UserCreate, UserResponse, EmailVerificationResponse
from src.email.service import create_verification_token, send_verification_email


router = APIRouter(
    tags=["Authentication"],
    prefix="/api/auth"
)


@router.post("/register", response_model=EmailVerificationResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    verification_token = create_verification_token()

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_hashed_password(user.password),
        full_name=user.full_name,
        phone=user.phone,
        verification_token=verification_token,
        role=user.role,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


    email_sent = send_verification_email(user.email, user.username, verification_token)

    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "email": user.email,
        "verification_sent": email_sent
    }

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    if user.is_verified:
        return {
            "message": "Email already verified",
            "verified": True,
            "redirect_to_login": True
        }
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return {
        "message": "Email verified successfully! You can now login.",
        "verified": True,
        "redirect_to_login": True
    }

@router.post("/resend-verification")
def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "Email already verified", "already_verified": True}
    
    
    verification_token = create_verification_token()
    user.verification_token = verification_token
    db.commit()
    
    
    email_sent = send_verification_email(user.email, user.username, verification_token)
    
    return {
        "message": "Verification email sent successfully",
        "email": email,
        "verification_sent": email_sent
    }


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

    return {"access_token": access_token, "token_type": "bearer"}
    

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):

    return current_user
