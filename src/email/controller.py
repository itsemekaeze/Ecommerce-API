from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.auth.service import verify_token
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.database.core import get_db
import jwt
from src.entities.users import UserModel
import traceback


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    tags=["Email Verification"]
)

@router.get("/verification", response_class=HTMLResponse)
async def email_verification(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        try:
            token_data = verify_token(token)
            user_id = int(token_data.id)
            
        except jwt.ExpiredSignatureError:
            return templates.TemplateResponse(
                "verification.html",
                {
                    "request": request,
                    "username": "User",
                    "message": "Verification link has expired. Please register again.",
                    "status": "error"
                },
                status_code=400
            )
        except jwt.InvalidTokenError:
            return templates.TemplateResponse(
                "verification.html",                
                {
                    "request": request,
                    "username": "User",
                    "message": "Invalid verification link. Please check your email or register again.",
                    "status": "error"
                },
                  status_code=404)
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            return templates.TemplateResponse(
                "verification.html",
                {
                    "request": request,
                    "username": "User",
                    "message": "User not found. Please register again.",
                    "status": "error"
                },
                status_code=404
            )
        
        if user.is_verified:
            return templates.TemplateResponse(
                "verification.html",
                {
                    "request": request,
                    "username": user.username,
                    "message": "Your email was already verified! You can login now.",
                    "status": "already_verified"
                }
            )
        
        user.is_verified = True
        db.commit()
        db.refresh(user)
        
        print(f"Email verified successfully for: {user.email}")
        
        return templates.TemplateResponse(
            "verification.html",
            {
                "request": request,
                "username": user.username,
                "message": "Email verified successfully! You can now login.",
                "status": "success"
            }
        )
    except Exception as e:
        print(f"Unexpected verification error: {str(e)}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "verification.html",
            {
                "request": request,
                "username": "User",
                "message": "An error occurred during verification. Please try again or contact support.",
                "status": "error"
            },
            status_code=500
        )
    