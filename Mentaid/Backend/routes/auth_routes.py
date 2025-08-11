"""
Authentication routes for user management and JWT-based authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
import logging

from models.user_models import (
    UserCreate, UserLogin, UserUpdate, PasswordChange, Token, TokenRefresh,
    UserResponse, AuthResponse, SuccessResponse, ErrorResponse, AdminPasswordReset,
    PasswordResetRequest, PasswordResetConfirm
)
from services.auth_service import AuthService
from middleware.auth_middleware import (
    AuthMiddleware, get_current_user_required, require_clinician_role,
    require_any_authenticated_user, rate_limiter
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/setup-database")
async def setup_database():
    """
    Setup database tables and RLS policies.
    This endpoint should be called once during initial setup.
    """
    try:
        result = await AuthService.create_user_table()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {"message": "Database setup completed successfully"}
        
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database setup failed: {str(e)}")

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: Request, user_data: UserCreate):
    """
    Register a new user.
    
    Args:
        request: FastAPI request object
        user_data: User registration data
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Rate limiting removed for better user experience
        
        result = await AuthService.signup(user_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Create response
        user_response = UserResponse(**result["user"])
        token_response = Token(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            role=result["role"],
            user_id=result["user"]["id"]
        )
        
        return AuthResponse(
            message=result["message"],
            user=user_response,
            tokens=token_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@router.post("/login", response_model=AuthResponse)
async def login(request: Request, user_data: UserLogin):
    """
    Authenticate a user.
    
    Args:
        request: FastAPI request object
        user_data: User login data
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Rate limiting removed for better user experience
        
        result = await AuthService.login(user_data)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create response
        user_response = UserResponse(**result["user"])
        token_response = Token(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            role=result["role"],
            user_id=result["user"]["id"]
        )
        
        logger.info(f"User {result['user']['email']} logged in successfully")
        
        return AuthResponse(
            message=result["message"],
            user=user_response,
            tokens=token_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during authentication")

@router.post("/login-form", response_model=AuthResponse)
async def login_form(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user using OAuth2 password form (for compatibility).
    
    Args:
        request: FastAPI request object
        form_data: OAuth2 form data
        
    Returns:
        AuthResponse: User data and authentication tokens
    """
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    return await login(request, user_data)

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token.
    
    Args:
        token_data: Refresh token data
        
    Returns:
        Token: New authentication tokens
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        result = await AuthService.refresh_token(token_data.refresh_token)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return Token(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            role=result["role"],
            user_id=""  # Not included in refresh response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during token refresh")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=get_current_user_required()):
    """
    Get current user information (protected route).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException: If user retrieval fails
    """
    try:
        user_id = current_user["sub"]
        result = await AuthService.get_user_by_id(user_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return UserResponse(**result["user"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user=get_current_user_required()
):
    """
    Update current user information.
    
    Args:
        update_data: Data to update
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Updated user data
        
    Raises:
        HTTPException: If update fails
    """
    try:
        user_id = current_user["sub"]
        result = await AuthService.update_user(user_id, update_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return UserResponse(**result["user"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: PasswordChange,
    current_user=get_current_user_required()
):
    """
    Change user password.
    
    Args:
        password_data: Current and new password
        current_user: Current authenticated user
        
    Returns:
        SuccessResponse: Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        user_id = current_user["sub"]
        result = await AuthService.change_password(user_id, password_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return SuccessResponse(message=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/me", response_model=SuccessResponse)
async def deactivate_current_user(current_user=get_current_user_required()):
    """
    Deactivate current user account.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        SuccessResponse: Success message
        
    Raises:
        HTTPException: If deactivation fails
    """
    try:
        user_id = current_user["sub"]
        result = await AuthService.deactivate_user(user_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return SuccessResponse(message=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate user endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Clinician-only routes
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    limit: int = 100,
    offset: int = 0,
    current_user=require_clinician_role()
):
    """
    Get all users (clinicians only).
    
    Args:
        limit: Number of users to return
        offset: Offset for pagination
        current_user: Current authenticated clinician
        
    Returns:
        List[UserResponse]: List of users
        
    Raises:
        HTTPException: If retrieval fails or access denied
    """
    try:
        user_role = current_user["role"]
        result = await AuthService.get_all_users(user_role, limit, offset)
        
        if result["status"] == "error":
            raise HTTPException(status_code=403, detail=result["message"])
        
        return [UserResponse(**user) for user in result["users"]]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all users endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user=require_clinician_role()
):
    """
    Get user by ID (clinicians only).
    
    Args:
        user_id: User ID to retrieve
        current_user: Current authenticated clinician
        
    Returns:
        UserResponse: User data
        
    Raises:
        HTTPException: If user not found or access denied
    """
    try:
        result = await AuthService.get_user_by_id(user_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return UserResponse(**result["user"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user by ID endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Password reset (user-initiated)
@router.post("/password/reset-request", response_model=SuccessResponse)
async def password_reset_request(request: Request, data: PasswordResetRequest):
    """
    Initiate a password reset. Returns generic success.
    In development, may include a reset_token for testing.
    """
    try:
        # Rate limiting removed for better user experience
        result = await AuthService.request_password_reset(data.email)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        # Allow passing through dev token if present
        msg = result.get("message", "If that email exists, a reset link has been initiated.")
        extra = {}
        if "reset_token" in result:
            extra["reset_token"] = result["reset_token"]
        return SuccessResponse(message=msg, data=extra or None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/password/reset-confirm", response_model=SuccessResponse)
async def password_reset_confirm(request: Request, data: PasswordResetConfirm):
    """
    Confirm password reset using token and new password.
    """
    try:
        # Rate limiting removed for better user experience
        result = await AuthService.confirm_password_reset(data.token, data.new_password)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"]) 
        return SuccessResponse(message=result.get("message", "Password has been reset successfully"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin/Development endpoints
@router.post("/admin/reset-password", response_model=SuccessResponse)
async def admin_reset_password(reset_data: AdminPasswordReset):
    """
    Reset user password (admin/development only).
    
    Args:
        reset_data: Password reset data
        
    Returns:
        SuccessResponse: Success message
    """
    try:
        result = await AuthService.admin_reset_password(reset_data.email, reset_data.new_password)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return SuccessResponse(message=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/admin/cleanup-test-users", response_model=SuccessResponse)
async def cleanup_test_users():
    """
    Remove test users (development only).
    
    Returns:
        SuccessResponse: Cleanup result
    """
    try:
        result = await AuthService.cleanup_test_users()
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return SuccessResponse(message=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup test users error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dict: Health status
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Test endpoints for development
@router.get("/test-auth")
async def test_auth(current_user=get_current_user_required()):
    """
    Test authentication (any authenticated user).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict: Test response with user info
    """
    return {
        "message": "Authentication successful",
        "user_id": current_user["sub"],
        "email": current_user["email"],
        "role": current_user["role"]
    }

@router.get("/test-clinician")
async def test_clinician(current_user=require_clinician_role()):
    """
    Test clinician-only access.
    
    Args:
        current_user: Current authenticated clinician
        
    Returns:
        Dict: Test response for clinicians
    """
    return {
        "message": "Clinician access successful",
        "user_id": current_user["sub"],
        "email": current_user["email"],
        "role": current_user["role"]
    }