"""
Configuration settings for the MirrorMind API.
"""
import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Application settings
    APP_NAME: str = "MirrorMind API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:7860",
        "https://*.hf.space",
        "https://*.railway.app",
        "https://*.render.com"
    ]
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database settings
    DATABASE_URL: Optional[str] = None  # For future use if needed
    MONGODB_URI: Optional[str] = None  # MongoDB connection string
    
    # Encryption settings
    ENCRYPTION_KEY: Optional[str] = None  # Data encryption key
    
    # External API settings
    OPENROUTER_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CLOUDINARY_URL: Optional[str] = None
    
    @field_validator('CORS_ORIGINS', mode='before')
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator('JWT_SECRET_KEY')
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key."""
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator('SUPABASE_URL')
    def validate_supabase_url(cls, v):
        """Validate Supabase URL."""
        if not v or not v.startswith('https://'):
            raise ValueError("SUPABASE_URL must be a valid HTTPS URL")
        return v
    
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Create settings instance
settings = Settings()

# Deployment-specific configurations
class DeploymentConfig:
    """
    Deployment-specific configuration helpers.
    """
    
    @staticmethod
    def get_railway_config():
        """Get Railway deployment configuration."""
        return {
            "host": "0.0.0.0",
            "port": int(os.getenv("PORT", 8000)),
            "cors_origins": [
                f"https://{os.getenv('RAILWAY_STATIC_URL', '')}",
                "http://localhost:3000"
            ]
        }
    
    @staticmethod
    def get_render_config():
        """Get Render deployment configuration."""
        return {
            "host": "0.0.0.0",
            "port": int(os.getenv("PORT", 10000)),
            "cors_origins": [
                f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', '')}",
                "http://localhost:3000"
            ]
        }
    
    @staticmethod
    def get_hf_spaces_config():
        """Get Hugging Face Spaces deployment configuration."""
        return {
            "host": "0.0.0.0",
            "port": 7860,
            "cors_origins": [
                "https://*.hf.space",
                "http://localhost:3000"
            ]
        }
    
    @staticmethod
    def get_production_cors_origins():
        """Get production CORS origins based on deployment platform."""
        origins = ["http://localhost:3000"]  # Always allow local development
        
        # Railway
        if os.getenv("RAILWAY_STATIC_URL"):
            origins.append(f"https://{os.getenv('RAILWAY_STATIC_URL')}")
        
        # Render
        if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
            origins.append(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}")
        
        # Hugging Face Spaces
        if os.getenv("SPACE_ID"):
            origins.extend(["https://*.hf.space", "https://huggingface.co"])
        
        # Custom domain
        if os.getenv("CUSTOM_DOMAIN"):
            origins.append(f"https://{os.getenv('CUSTOM_DOMAIN')}")
        
        return origins

# Security configurations
class SecurityConfig:
    """
    Security-related configuration.
    """
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = False
    
    # Session settings
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Rate limiting
    AUTH_RATE_LIMIT = 20  # requests per hour
    API_RATE_LIMIT = 1000  # requests per hour
    
    # Trusted hosts (for production)
    TRUSTED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "*.railway.app",
        "*.render.com",
        "*.hf.space"
    ]

# Feature flags
class FeatureFlags:
    """
    Feature flags for enabling/disabling functionality.
    """
    
    ENABLE_REGISTRATION = True
    ENABLE_PASSWORD_RESET = True
    ENABLE_EMAIL_VERIFICATION = False
    ENABLE_TWO_FACTOR_AUTH = False
    ENABLE_AUDIT_LOGGING = True
    ENABLE_RATE_LIMITING = True
    ENABLE_REQUEST_LOGGING = True
    ENABLE_HEALTH_CHECKS = True

# Export commonly used settings
__all__ = [
    "settings",
    "DeploymentConfig",
    "SecurityConfig",
    "FeatureFlags"
]