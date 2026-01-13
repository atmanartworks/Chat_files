"""
Authentication module for user login and registration.
"""
from fastapi import Depends, HTTPException, status  # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # type: ignore
from jose import JWTError, jwt  # type: ignore
import bcrypt  # type: ignore
from datetime import datetime, timedelta
from sqlalchemy.orm import Session  # type: ignore
from typing import Optional, Union
from .database import get_db, User
from .supabase_db import (
    get_user_by_username as supabase_get_user_by_username,
    get_user_by_email as supabase_get_user_by_email,
    check_password_hash as supabase_check_password
)
import os

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Decode the hashed password from bytes if needed
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Truncate password to 72 bytes (bcrypt limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Optional[Session], username: str) -> Optional[Union[User, dict]]:
    """Get user by username - uses Supabase if available, otherwise SQLAlchemy."""
    use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    if use_supabase:
        user_dict = supabase_get_user_by_username(username)
        if user_dict:
            # Convert dict to User-like object for compatibility
            user = type('User', (), user_dict)()
            return user
        return None
    else:
        if db:
            return db.query(User).filter(User.username == username).first()
        return None

def get_user_by_email(db: Optional[Session], email: str) -> Optional[Union[User, dict]]:
    """Get user by email - uses Supabase if available, otherwise SQLAlchemy."""
    use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    if use_supabase:
        user_dict = supabase_get_user_by_email(email)
        if user_dict:
            user = type('User', (), user_dict)()
            return user
        return None
    else:
        if db:
            return db.query(User).filter(User.email == email).first()
        return None

def authenticate_user(db: Optional[Session], username: str, password: str) -> Optional[Union[User, dict]]:
    """Authenticate a user - uses Supabase if available, otherwise SQLAlchemy."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    if use_supabase:
        # User is a dict-like object from Supabase
        password_hash = getattr(user, 'password_hash', None) or (user if isinstance(user, dict) else {}).get('password_hash')
        if not password_hash:
            return None
        if supabase_check_password(password_hash, password):
            return user
        return None
    else:
        # User is SQLAlchemy User object
        if not verify_password(password, user.password_hash):
            return None
        return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Optional[Session] = Depends(get_db)) -> Union[User, dict]:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user
