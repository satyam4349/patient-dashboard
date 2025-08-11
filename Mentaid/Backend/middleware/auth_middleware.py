"""
Authentication middleware for JWT verification and role-based access control.
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import logging

from utils.security import decode_access_token
from models.user_models import TokenData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """Authentication middleware class."""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """
        Verify JWT token and return user data.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Dict: User data from token
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        result = decode_access_token(token)
        
        if result["status"] == "error":
            logger.warning(f"Token verification failed: {result['message']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"],
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return result["data"]
    
    @staticmethod
    async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
        """
        Extract user from request based on JWT token (non-blocking).
        
        Args:
            request: FastAPI request object
            
        Returns:
            Optional[Dict]: User data if token is valid, None otherwise
        """
        try:
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            result = decode_access_token(token)
            
            if result["status"] == "error":
                return None
            
            return result["data"]
        except Exception as e:
            logger.error(f"Error extracting user from request: {str(e)}")
            return None
    
    @staticmethod
    def require_roles(allowed_roles: List[str]):
        """
        Dependency factory for role-based access control.
        
        Args:
            allowed_roles: List of allowed roles
            
        Returns:
            Dependency function
        """
        async def role_checker(current_user: Dict[str, Any] = Depends(AuthMiddleware.verify_token)) -> Dict[str, Any]:
            """
            Check if user has required role.
            
            Args:
                current_user: Current user data from token
                
            Returns:
                Dict: Current user data
                
            Raises:
                HTTPException: If user doesn't have required role
            """
            user_role = current_user.get("role")
            
            if user_role not in allowed_roles:
                logger.warning(f"Access denied for role {user_role}. Required: {allowed_roles}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
                )
            
            return current_user
        
        return role_checker


# Define dependency functions outside the class to avoid circular references
def require_auth(current_user: Dict[str, Any] = Depends(AuthMiddleware.verify_token)) -> Dict[str, Any]:
    """
    Dependency that requires authentication.
    
    Args:
        current_user: Current user data from token
        
    Returns:
        Dict: Current user data
    """
    return current_user


def require_clinician(current_user: Dict[str, Any] = Depends(AuthMiddleware.require_roles(["clinician"]))) -> Dict[str, Any]:
    """
    Dependency that requires clinician role.
    
    Args:
        current_user: Current user data from token
        
    Returns:
        Dict: Current user data
    """
    return current_user


def require_user_or_clinician(current_user: Dict[str, Any] = Depends(AuthMiddleware.require_roles(["regular_user", "clinician"]))) -> Dict[str, Any]:
    """
    Dependency that requires regular user or clinician role.
    
    Args:
        current_user: Current user data from token
        
    Returns:
        Dict: Current user data
    """
    return current_user


# Add these as class methods for backward compatibility
AuthMiddleware.require_auth = staticmethod(require_auth)
AuthMiddleware.require_clinician = staticmethod(require_clinician)
AuthMiddleware.require_user_or_clinician = staticmethod(require_user_or_clinician)

# Convenience functions for common use cases
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user without raising exceptions."""
    return await AuthMiddleware.get_current_user(request)

def get_current_user_required() -> Dict[str, Any]:
    """Get current user with authentication required."""
    return Depends(AuthMiddleware.require_auth)

def require_clinician_role() -> Dict[str, Any]:
    """Require clinician role."""
    return Depends(AuthMiddleware.require_clinician)

def require_any_authenticated_user() -> Dict[str, Any]:
    """Require any authenticated user (regular_user or clinician)."""
    return Depends(AuthMiddleware.require_user_or_clinician)

# Rate limiting middleware (basic implementation)
class RateLimitMiddleware:
    """Basic rate limiting middleware."""
    
    def __init__(self):
        self.requests = {}
    
    async def check_rate_limit(self, request: Request, max_requests: int = 100, window_seconds: int = 3600):
        """
        Check rate limit for IP address.
        
        Args:
            request: FastAPI request object
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        import time
        
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: [(timestamp, count) for timestamp, count in requests 
                 if current_time - timestamp < window_seconds]
            for ip, requests in self.requests.items()
        }
        
        # Count requests for this IP
        ip_requests = self.requests.get(client_ip, [])
        total_requests = sum(count for _, count in ip_requests)
        
        if total_requests >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append((current_time, 1))

# Global rate limiter instance
rate_limiter = RateLimitMiddleware()