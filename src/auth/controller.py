from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.entities.users import User, UserRole
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
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    verification_token = create_verification_token()
    hashed_password = get_hashed_password(user.password)
    
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_active=True,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    email_result = send_verification_email(user.email, verification_token)
    
    if email_result["success"]:
        return EmailVerificationResponse(
            message="Registration successful! Please check your email to verify your account.",
            email=user.email,
            status="pending_verification"
        )
    else:
        return EmailVerificationResponse(
            message="Registration failed! Email could not be sent. Please use the verification link below.",
            email=user.email,
            status="email_failed"
        )


@router.get("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if user.is_verified:
        return EmailVerificationResponse(message="Email already verified", email=user.email, status="already_verified")
    
    user.is_verified = True
    user.verification_token = None
    db.commit()
    
    return EmailVerificationResponse(message="Email verified successfully! You can now login.", email=user.email, status="verified")

@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification(email: EmailStr, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == email.lower()).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return EmailVerificationResponse(message="Email is already verified", email=user.email, status="already_verified")
    
    new_token = create_verification_token()
    user.verification_token = new_token
    db.commit()
    
    email_result = send_verification_email(user.email, new_token)
    
    if email_result["success"]:
        return EmailVerificationResponse(message="Verification email resent!", email=user.email, status="email_resent")
    else:
        return EmailVerificationResponse(
            message="Could not send email. Please use the verification link below.",
            email=user.email,
            status="email_failed"
        )


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
    



