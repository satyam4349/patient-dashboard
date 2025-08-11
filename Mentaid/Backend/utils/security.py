"""
Security utilities for password hashing and JWT token management.
"""
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Union
from jose import jwt, JWTError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes by default
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days for refresh tokens

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with salt.
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password (str): Plain text password
        hashed_password (str): Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data (Dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Custom expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    # Create the JWT token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        data (Dict): Data to encode in the token
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Union[str, Dict]]:
    """
    Decode and verify a JWT token.
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        Dict: Result with status and data/message
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return {"status": "error", "message": "Token has expired"}
        
        # Check token type
        token_type = payload.get("type", "access")
        if token_type != "access":
            return {"status": "error", "message": "Invalid token type"}
            
        return {"status": "success", "data": payload}
        
    except JWTError as e:
        return {"status": "error", "message": f"Invalid token: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Token validation error: {str(e)}"}

def decode_refresh_token(token: str) -> Dict[str, Union[str, Dict]]:
    """
    Decode and verify a JWT refresh token.
    
    Args:
        token (str): JWT refresh token to decode
        
    Returns:
        Dict: Result with status and data/message
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return {"status": "error", "message": "Refresh token has expired"}
        
        # Check token type
        token_type = payload.get("type", "access")
        if token_type != "refresh":
            return {"status": "error", "message": "Invalid token type"}
            
        return {"status": "success", "data": payload}
        
    except JWTError as e:
        return {"status": "error", "message": f"Invalid refresh token: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Refresh token validation error: {str(e)}"}

def validate_password_strength(password: str) -> Dict[str, Union[bool, str]]:
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
        
    Returns:
        Dict: Validation result with is_valid and message
    """
    if len(password) < 8:
        return {"is_valid": False, "message": "Password must be at least 8 characters long"}
    
    if not any(c.isupper() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one uppercase letter"}
    
    if not any(c.islower() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one lowercase letter"}
    
    if not any(c.isdigit() for c in password):
        return {"is_valid": False, "message": "Password must contain at least one digit"}
    
    return {"is_valid": True, "message": "Password is strong"}