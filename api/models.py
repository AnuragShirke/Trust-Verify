"""
Database models for the Fake News Detector API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class User(UserBase):
    """User model."""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset model."""
    token: str
    new_password: str


class TokenData(BaseModel):
    """Token data model."""
    email: Optional[str] = None
    exp: Optional[datetime] = None


class AnalysisBase(BaseModel):
    """Base analysis model."""
    content_type: str = "text"  # "text" or "url"
    content: str
    title: Optional[str] = None
    url: Optional[str] = None


class AnalysisCreate(AnalysisBase):
    """Analysis creation model."""
    user_id: str


class Analysis(AnalysisBase):
    """Analysis model."""
    id: str
    user_id: str
    prediction: str
    confidence: float
    trust_score: float
    trust_level: str
    created_at: datetime
    factors: dict
    details: dict

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    """User profile model."""
    user: User
    analysis_count: int
    recent_analyses: List[Analysis]
    average_trust_score: float
