"""
Main FastAPI application entry point.

This file creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- API route registration
- Database initialization
- Error handling
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

# Import our modules
from .core.config import settings
from .core.database import init_db
from .api import auth, opportunities

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    This function runs when the application starts up and shuts down.
    It's used for:
    - Database initialization
    - Resource cleanup
    - Health checks
    """
    # Startup
    logger.info("Starting Campus Climb application...")
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("Campus Climb application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Campus Climb application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",  # Swagger UI endpoint
    redoc_url="/redoc",  # ReDoc endpoint
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
# CORS allows your frontend (running on localhost:3000) to communicate with your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions globally.
    
    This ensures consistent error response format across all endpoints.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions globally.
    
    This catches any exceptions not handled by specific handlers
    and returns a generic error response.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "path": request.url.path
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    This endpoint is used by:
    - Load balancers to check if the service is running
    - Monitoring tools to track application health
    - DevOps teams for deployment verification
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": "2024-01-01T00:00:00Z"  # You could use datetime.now().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing basic application information.
    
    This is the first endpoint users see when they visit your API.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "description": settings.app_description,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
# This registers all the endpoints from our API modules
app.include_router(
    auth.router,
    prefix=settings.api_v1_prefix,
    tags=["Authentication"]
)

app.include_router(
    opportunities.router,
    prefix=settings.api_v1_prefix,
    tags=["Opportunities"]
)


# Note: Startup and shutdown events are now handled by the lifespan manager above
# This provides better control over application lifecycle


if __name__ == "__main__":
    """
    Entry point when running the application directly.
    
    This allows you to run the application with:
    python -m app.main
    
    In production, you'd use uvicorn instead.
    """
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
