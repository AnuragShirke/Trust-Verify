"""
Authentication module for the Fake News Detector API.

This module provides functions for authenticating users.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from database import get_user_by_email, verify_password, update_user_last_login
from models import TokenData, User

# JWT configuration
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate a user.
    
    Args:
        email: The email of the user
        password: The password of the user
        
    Returns:
        dict: The authenticated user, or None if authentication failed
    """
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: The expiration time delta
        
    Returns:
        str: The access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from a token.
    
    Args:
        token: The access token
        
    Returns:
        User: The current user
        
    Raises:
        HTTPException: If the token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    
    # Update last login time
    update_user_last_login(user["id"])
    
    return User(
        id=user["id"],
        email=user["email"],
        full_name=user.get("full_name", user.get("username", "")),  # Fallback to username if full_name is not available
        is_google_user=user.get("is_google_user", False),
        created_at=datetime.fromisoformat(user["created_at"]),
        last_login=datetime.fromisoformat(user["last_login"]) if user["last_login"] else None,
        is_active=user["is_active"]
    )
