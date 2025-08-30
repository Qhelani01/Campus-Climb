"""
Authentication service for user management.

This service handles:
- User registration and validation
- Password hashing and verification
- JWT token creation and validation
- WVSU email domain verification
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..core.config import settings
from ..models.user import User, UserCreate, UserResponse, TokenData
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Password hashing context
# bcrypt is the industry standard for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Service class for authentication operations.
    
    This class encapsulates all authentication logic, making it
    easy to test and maintain. It follows the service layer pattern
    which separates business logic from API endpoints.
    """
    
    def __init__(self):
        """Initialize the authentication service."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        This function safely compares passwords without storing
        the plain text version in memory.
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        bcrypt automatically handles salt generation and is
        designed to be computationally expensive to prevent
        brute force attacks.
        """
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing password"
            )
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        JWT tokens are self-contained and include:
        - User identification (email, user_id)
        - Expiration time
        - Issued at time
        - Digital signature for security
        """
        try:
            to_encode = data.copy()
            
            # Set expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire})
            
            # Create JWT token
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user: {data.get('email', 'unknown')}")
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating access token"
            )
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        This function validates the token's signature and
        extracts the user information from the payload.
        """
        try:
            # Decode the JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract user data
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                logger.warning("Invalid token payload")
                return None
            
            # Create token data object
            token_data = TokenData(email=email, user_id=user_id)
            logger.info(f"Token verified for user: {email}")
            return token_data
            
        except JWTError as e:
            logger.warning(f"JWT token error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        This function:
        1. Finds the user by email
        2. Verifies the password hash
        3. Returns the user if authentication succeeds
        """
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                logger.warning(f"Login attempt with non-existent email: {email}")
                return None
            
            # Verify password
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for user: {email}")
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {email}")
                return None
            
            logger.info(f"Successful authentication for user: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None
    
    def create_user(self, db: Session, user_create: UserCreate) -> UserResponse:
        """
        Create a new user account.
        
        This function:
        1. Validates the WVSU email domain
        2. Checks for existing users
        3. Hashes the password
        4. Creates the user record
        """
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_create.email) | (User.username == user_create.username)
            ).first()
            
            if existing_user:
                if existing_user.email == user_create.email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            
            # Validate WVSU email domain
            if not user_create.email.endswith(f"@{settings.allowed_email_domain}"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Only {settings.allowed_email_domain} email addresses are allowed"
                )
            
            # Hash the password
            hashed_password = self.get_password_hash(user_create.password)
            
            # Create user object
            db_user = User(
                email=user_create.email,
                username=user_create.username,
                hashed_password=hashed_password,
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                major=user_create.major,
                graduation_year=user_create.graduation_year,
                bio=user_create.bio,
                is_active=True,
                is_verified=False  # Email verification could be added later
            )
            
            # Save to database
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Created new user account: {user_create.email}")
            
            # Return user response (without password)
            return UserResponse.from_orm(db_user)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )
    
    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """
        Get the current authenticated user from a JWT token.
        
        This function is used as a dependency in protected endpoints
        to ensure the user is authenticated.
        """
        try:
            # Verify the token
            token_data = self.verify_token(token)
            if token_data is None:
                return None
            
            # Get user from database
            user = db.query(User).filter(User.id == token_data.user_id).first()
            
            if user is None:
                logger.warning(f"Token references non-existent user: {token_data.user_id}")
                return None
            
            if not user.is_active:
                logger.warning(f"Token for inactive user: {user.email}")
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None


# Create a global instance of the auth service
auth_service = AuthService()
