"""
Database connection and session management.

This module handles:
- Database engine creation
- Session management
- Connection pooling
- Database initialization
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the base class for all database models
Base = declarative_base()


def get_database_url() -> str:
    """
    Get the database URL from settings.
    
    For development, we'll use SQLite. In production, you'd use
    PostgreSQL or MySQL for better performance and features.
    """
    return settings.database_url


def create_database_engine():
    """
    Create the database engine with appropriate configuration.
    
    The engine is the low-level interface to the database that handles:
    - Connection pooling
    - SQL compilation
    - Transaction management
    """
    database_url = get_database_url()
    
    if database_url.startswith("sqlite"):
        # SQLite configuration for development
        engine = create_engine(
            database_url,
            connect_args={
                "check_same_thread": False,  # Allow multiple threads
            },
            poolclass=StaticPool,  # Simple connection pooling for SQLite
            echo=settings.debug,  # Log SQL queries in debug mode
        )
        logger.info("Created SQLite database engine")
    else:
        # PostgreSQL/MySQL configuration for production
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            echo=settings.debug, # Log SQL queries in debug mode
        )
        logger.info("Created production database engine")
    
    return engine


# Create the database engine
engine = create_database_engine()

# Create session factory
# This factory creates new database sessions when called
SessionLocal = sessionmaker(
    autocommit=False,      # Don't auto-commit transactions
    autoflush=False,       # Don't auto-flush changes
    bind=engine,           # Use our database engine
)


def get_db() -> Session:
    """
    Dependency function to get database session.
    
    This function is used by FastAPI to inject database sessions
    into API endpoints. It ensures proper session management
    and cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    
    This function creates the database schema based on the
    SQLAlchemy models we've defined. In production, you'd use
    Alembic for database migrations instead.
    """
    try:
        # Import all models to ensure they're registered
        from ..models import user, opportunity
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data! Only use in development.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_db():
    """
    Initialize the database.
    
    This function sets up the database for first use.
    In a real application, you'd also seed it with initial data.
    """
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
