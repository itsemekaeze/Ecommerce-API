import bcrypt
import hashlib
from fastapi import HTTPException, status, Depends
import jwt
from src.entities.users import User, UserRole
from dotenv import dotenv_values
from datetime import datetime, timedelta
from src.auth.models import TokenData
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from src.database.core import get_db


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

config = dotenv_values(".env")


def get_hashed_password(password: str):
    
    prehash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehash.encode('utf-8'), salt)

    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str):
    prehash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return bcrypt.checkpw(prehash.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config["SECRET"], algorithm=config["ALGORITHM"])

    return encoded_jwt


def verify_token(token: str) :

    try:
        payload = jwt.decode(token, config["SECRET"], algorithms=[config["ALGORITHM"]])
        
        user_id: str = payload.get("id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
                
        return TokenData(id=str(user_id))
        
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
 
        )
    

def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):

    token_data = verify_token(token)

    user = db.query(User).filter(User.id == int(token_data.id)).first()

    return user


def require_role(allowed_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker



def require_verified(current_user: User = Depends(get_current_user)):
    if not current_user.is_verified:
        raise HTTPException(
            status_code=403, 
            detail="Email verification required. Please verify your email to access this feature."
        )
    
    return current_user