"""
Main FastAPI application with authentication and mental health analysis.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
import uvicorn

# Import routes
from routes.auth_routes import router as auth_router
from routes.patient_routes import router as patient_router
from routes.agent_routes import router as agent_router
from routes.ai_companion_routes import router as ai_companion_router
from routes.diagnostics_routes import router as diagnostics_router
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting MirrorMind API...")
    
    # Initialize database tables if needed
    try:
        from services.auth_service import AuthService
        setup_result = await AuthService.create_user_table()
        if setup_result["status"] == "success":
            logger.info("Database tables verified/created successfully")
        else:
            logger.warning(f"Database setup warning: {setup_result['message']}")
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
    
    logger.info("MirrorMind API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MirrorMind API...")

# Create FastAPI application
app = FastAPI(
    title="MirrorMind API",
    description="Mental Health Analysis API with JWT Authentication and Role-Based Access Control",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this for production
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed messages.
    """
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent format.
    """
    logger.warning(f"HTTP exception on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": getattr(exc, 'error_code', None)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    """
    logger.error(f"Unexpected error on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests for monitoring.
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Include routers
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(agent_router)
app.include_router(ai_companion_router)
app.include_router(diagnostics_router)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to MirrorMind API",
        "version": "1.0.0",
        "description": "Mental Health Analysis API with JWT Authentication",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "mirrormind-api",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# API status endpoint
@app.get("/status")
async def api_status():
    """
    Detailed API status endpoint.
    """
    import psutil
    import platform
    
    return {
        "api": {
            "status": "running",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        },
        "system": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        },
        "database": {
            "status": "connected",  # You can add actual database health check here
            "type": "supabase"
        }
    }

# Configuration endpoint (non-sensitive info only)
@app.get("/config")
async def get_config():
    """
    Get non-sensitive configuration information.
    """
    return {
        "cors_origins": [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:7860"
        ],
        "features": {
            "authentication": True,
            "role_based_access": True,
            "rate_limiting": True,
            "request_logging": True
        },
        "supported_roles": ["regular_user", "clinician"],
        "token_expiry_minutes": 30
    }

# Add time import for middleware
import time

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )