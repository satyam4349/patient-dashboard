"""
Pydantic models for user authentication and management.
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr

class UserCreate(UserBase):
    """Model for user registration."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Literal["regular_user", "clinician"] = Field(..., description="User role")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate user role."""
        allowed_roles = ['regular_user', 'clinician']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

class UserLogin(UserBase):
    """Model for user login."""
    password: str

class UserUpdate(BaseModel):
    """Model for updating user information."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    """Model for password change."""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

class Token(BaseModel):
    """Model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    role: str
    user_id: str

class TokenRefresh(BaseModel):
    """Model for token refresh request."""
    refresh_token: str

class TokenData(BaseModel):
    """Model for token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserResponse(UserBase):
    """Model for user response (excludes sensitive data)."""
    id: str
    role: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    """Extended user profile model."""
    last_login: Optional[datetime] = None
    login_count: int = 0

# Error response models
class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    detail: str
    errors: list

# Success response models
class SuccessResponse(BaseModel):
    """Standard success response model."""
    message: str
    data: Optional[dict] = None

class AuthResponse(BaseModel):
    """Authentication response model."""
    message: str
    user: UserResponse
    tokens: Token

# Admin models
class AdminPasswordReset(BaseModel):
    """Model for admin password reset."""
    email: EmailStr
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

# Password reset models (user-initiated flow)
class PasswordResetRequest(BaseModel):
    """Request model to initiate password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm model for password reset with token and new password."""
    token: str
    new_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')

        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')

        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')

        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')

        return v