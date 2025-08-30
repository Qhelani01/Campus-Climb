"""
User model for authentication and user management.

This model defines the structure for user accounts, including:
- Basic user information
- Authentication credentials
- WVSU email validation
- Account status and timestamps
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


# Create the base class for all database models
Base = declarative_base()


class User(Base):
    """
    SQLAlchemy model for the users table.
    
    This represents the actual database table structure and handles
    the relationship between Python objects and database records.
    """
    
    __tablename__ = "users"
    
    # Primary key - unique identifier for each user
    id = Column(Integer, primary_key=True, index=True)
    
    # User identification
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    
    # User profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    major = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional info
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)


# Pydantic models for API requests/responses
class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Model for creating new users."""
    password: str
    
    @validator('email')
    def validate_wvsu_email(cls, v):
        """
        Validate that the email ends with @wvstateu.edu
        
        This ensures only WVSU students can register for the platform.
        """
        if not v.endswith('@wvstateu.edu'):
            raise ValueError('Only WVSU email addresses are allowed')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """
        Validate password strength.
        
        Ensures passwords are at least 8 characters long and contain
        a mix of letters, numbers, and special characters.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """Model for updating user information."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserResponse(UserBase):
    """Model for API responses with user data."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        # Enable ORM mode for SQLAlchemy integration
        from_attributes = True


class UserLogin(BaseModel):
    """Model for user login requests."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Model for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Model for token payload data."""
    email: Optional[str] = None
    user_id: Optional[int] = None
