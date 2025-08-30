"""
Configuration settings for the Campus Climb application.

This file centralizes all configuration settings including:
- Database connection
- Security settings
- API configuration
- Environment-specific settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings using Pydantic for validation.
    
    Pydantic automatically validates that all required settings are present
    and converts them to the correct types.
    """
    
    # Application metadata
    app_name: str = "Campus Climb"
    app_version: str = "1.0.0"
    app_description: str = "WVSU Opportunities Platform"
    
    # API configuration
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database configuration
    database_url: str = "sqlite:///./campus_climb.db"
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # WVSU email domain validation
    allowed_email_domain: str = "wvstateu.edu"
    
    class Config:
        # Load environment variables from .env file
        env_file = ".env"
        # Allow case-insensitive environment variable names
        case_sensitive = False


# Create a global settings instance
settings = Settings()

# Override settings with environment variables if they exist
if os.getenv("SECRET_KEY"):
    settings.secret_key = os.getenv("SECRET_KEY")
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")
if os.getenv("DEBUG"):
    settings.debug = os.getenv("DEBUG").lower() == "true"
