"""
Authentication API endpoints.

This module provides REST API endpoints for:
- User registration
- User login
- Profile management
- Token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

# Import our modules
from ..core.database import get_db
from ..services.auth import auth_service
from ..models.user import UserCreate, UserResponse, UserLogin, Token, UserUpdate, User

# Set up logging
logger = logging.getLogger(__name__)

# Create router for authentication endpoints
router = APIRouter()

# HTTP Bearer token security scheme
security = HTTPBearer()


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function to get the current authenticated user.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Validates the token
    3. Returns the user if authentication succeeds
    4. Raises an HTTPException if authentication fails
    
    It's used as a dependency in protected endpoints to ensure
    only authenticated users can access them.
    """
    try:
        # Get token from credentials
        token = credentials.credentials
        
        # Get current user from token
        user = auth_service.get_current_user(db, token)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    This endpoint:
    1. Validates the user data (email, password, etc.)
    2. Checks for existing users
    3. Hashes the password securely
    4. Creates the user account
    5. Returns the user profile (without password)
    
    Only WVSU email addresses are accepted.
    """
    try:
        logger.info(f"User registration attempt: {user_create.email}")
        
        # Create user using auth service
        user = auth_service.create_user(db, user_create)
        
        logger.info(f"User registered successfully: {user.email}")
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    This endpoint:
    1. Validates email and password
    2. Authenticates the user
    3. Creates and returns a JWT access token
    
    The token is used for subsequent authenticated requests.
    """
    try:
        logger.info(f"Login attempt: {user_login.email}")
        
        # Authenticate user
        user = auth_service.authenticate_user(db, user_login.email, user_login.password)
        
        if not user:
            logger.warning(f"Failed login attempt: {user_login.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = auth_service.access_token_expire_minutes
        access_token = auth_service.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=None  # Use default expiration
        )
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": access_token_expires * 60  # Convert to seconds
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile.
    
    This endpoint returns the profile of the currently authenticated user.
    It's protected and requires a valid JWT token.
    """
    try:
        logger.info(f"Profile request for user: {current_user.email}")
        return current_user
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile.
    
    This endpoint allows users to update their profile information.
    It's protected and requires a valid JWT token.
    """
    try:
        logger.info(f"Profile update request for user: {current_user.email}")
        
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        # Save changes to database
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Profile updated successfully for user: {current_user.email}")
        return current_user
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user profile"
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """
    Logout the current user.
    
    This endpoint marks the user as logged out.
    Note: JWT tokens are stateless, so the client should discard the token.
    In a more sophisticated system, you might implement a token blacklist.
    """
    try:
        logger.info(f"User logout: {current_user.email}")
        
        # In a real application, you might:
        # - Add the token to a blacklist
        # - Update user's last logout time
        # - Send logout notification
        
        return {
            "message": "Successfully logged out",
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )


@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user email address.
    
    This endpoint would be used to verify email addresses when users
    click verification links sent to their email.
    
    Note: This is a placeholder for future email verification functionality.
    """
    try:
        # TODO: Implement email verification logic
        # This would involve:
        # 1. Decoding the verification token
        # 2. Finding the user
        # 3. Marking their email as verified
        
        return {
            "message": "Email verification endpoint",
            "note": "This functionality will be implemented in a future update"
        }
        
    except Exception as e:
        logger.error(f"Error in email verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during email verification"
        )
