from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, TokenData
import os
from dotenv import load_dotenv
import logging

# Add logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Debug log the secret key
logger.debug(f"JWT_SECRET loaded: {SECRET_KEY is not None}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        logger.debug(f"Token received: {token[:50]}...")
        
        # First try to get unverified claims to see token structure
        try:
            unverified = jwt.get_unverified_claims(token)
            logger.debug(f"Unverified payload: {unverified}")
        except Exception as e:
            logger.debug(f"Could not get unverified claims: {e}")
        
        # Now decode with verification
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug(f"Decoded payload: {payload}")
        
        # Handle both FastAPI format (sub: email) and Express format (email field)
        email: str = payload.get("sub") or payload.get("email")
        logger.debug(f"Extracted email: {email}")
        
        if email is None:
            logger.debug("No email found in token")
            raise credentials_exception
            
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.debug(f"JWT Error: {e}")
        raise credentials_exception
    
    user = get_user_by_email(db, email=token_data.email)
    logger.debug(f"User lookup result: {user.email if user else 'None'}")
    
    if user is None:
        logger.debug("User not found in database")
        raise credentials_exception
    
    logger.debug("Authentication successful")
    return user