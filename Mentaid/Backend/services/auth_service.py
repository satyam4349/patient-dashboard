"""
Authentication service with Supabase integration.
"""
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone
import logging

# Import the patch before supabase to avoid realtime import issues
from utils.supabase_patch import patch_supabase_realtime
from supabase import create_client, Client
from dotenv import load_dotenv
import secrets
import hashlib

from utils.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models.user_models import UserCreate, UserLogin, UserUpdate, PasswordChange

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

if not all([supabase_url, supabase_service_key]):
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")

# Create Supabase clients
supabase_admin: Client = create_client(supabase_url, supabase_service_key)
supabase_anon: Client = create_client(supabase_url, supabase_anon_key)

class AuthService:
    """Authentication service class."""
    
    @staticmethod
    async def create_user_table():
        """
        Check if users table exists and provide setup instructions.
        Since Supabase doesn't support direct table creation via REST API,
        this method checks table existence and provides setup guidance.
        """
        try:
            # Try to check if users table exists by attempting a simple query
            result = supabase_admin.table('users').select('id').limit(1).execute()
            
            # If we get here without exception, table exists
            logger.info("Users table already exists")
            return {"status": "success", "message": "Users table is already set up"}
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check if error is due to missing table (various error formats)
            table_not_found_indicators = [
                'relation "users" does not exist',
                'table "users" does not exist',
                'could not find the table',
                'pgrst205',  # PostgREST error code for table not found
                'schema cache'
            ]
            
            if any(indicator in error_message for indicator in table_not_found_indicators):
                logger.error("Users table does not exist")
                return {
                    "status": "error", 
                    "message": "Users table not found. Please run the database migration first.",
                    "instructions": {
                        "step1": "Go to your Supabase dashboard",
                        "step2": "Navigate to SQL Editor",
                        "step3": "Run the SQL migration provided in database/migrations/001_create_users_table.sql",
                        "step4": "Or use the Supabase CLI: supabase db push"
                    }
                }
            else:
                logger.error(f"Error checking user table: {str(e)}")
                return {"status": "error", "message": f"Database connection failed: {str(e)}"}
    
    @staticmethod
    async def signup(user_data: UserCreate) -> Dict:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict: Registration result with tokens
        """
        try:
            # Check if user already exists
            existing_user = supabase_admin.table('users').select('id, email').eq('email', user_data.email).execute()
            
            if existing_user.data:
                return {"status": "error", "message": "User with this email already exists"}
            
            # Hash the password
            hashed_password = hash_password(user_data.password)
            
            # Insert new user
            user_insert_data = {
                "email": user_data.email,
                "password_hash": hashed_password,
                "role": user_data.role,
                "full_name": user_data.full_name,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "login_count": 0
            }
            
            result = supabase_admin.table('users').insert(user_insert_data).execute()
            
            if not result.data:
                return {"status": "error", "message": "Failed to create user"}
            
            user = result.data[0]
            
            # Generate tokens
            token_data = {
                "sub": user["id"], 
                "email": user["email"], 
                "role": user["role"]
            }
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
            refresh_token = create_refresh_token(data=token_data)
            
            # Remove sensitive data from user object
            user_response = {k: v for k, v in user.items() if k != 'password_hash'}
            
            return {
                "status": "success",
                "message": "User registered successfully",
                "user": user_response,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "role": user["role"]
            }
                
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return {"status": "error", "message": f"Registration failed: {str(e)}"}
    
    @staticmethod
    async def login(user_data: UserLogin) -> Dict:
        """
        Authenticate a user.
        
        Args:
            user_data: User login data
            
        Returns:
            Dict: Authentication result with tokens
        """
        try:
            # First check if user exists at all
            user_check = supabase_admin.table('users').select('*').eq('email', user_data.email).execute()
            
            if not user_check.data:
                logger.warning(f"Login attempt for non-existent user: {user_data.email}")
                return {"status": "error", "message": "Invalid email or password"}
            
            # Check if user is active
            result = supabase_admin.table('users').select('*').eq('email', user_data.email).eq('is_active', True).execute()
            
            if not result.data:
                logger.warning(f"Login attempt for inactive user: {user_data.email}")
                return {"status": "error", "message": "Account is inactive. Please contact support."}
            
            user = result.data[0]
            
            # Verify password
            if not verify_password(user_data.password, user['password_hash']):
                logger.warning(f"Invalid password attempt for user: {user_data.email}")
                return {"status": "error", "message": "Invalid email or password"}
            
            # Update login statistics
            login_update = {
                "last_login": datetime.now(timezone.utc).isoformat(),
                "login_count": user.get('login_count', 0) + 1,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            supabase_admin.table('users').update(login_update).eq('id', user['id']).execute()
            
            # Generate tokens
            token_data = {
                "sub": user["id"], 
                "email": user["email"], 
                "role": user["role"]
            }
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
            refresh_token = create_refresh_token(data=token_data)
            
            # Remove sensitive data from user object
            user_response = {k: v for k, v in user.items() if k != 'password_hash'}
            user_response.update(login_update)
            
            return {
                "status": "success",
                "message": "Login successful",
                "user": user_response,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "role": user["role"]
            }
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {"status": "error", "message": f"Authentication failed: {str(e)}"}
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict: New tokens or error
        """
        try:
            # Decode refresh token
            result = decode_refresh_token(refresh_token)
            
            if result["status"] == "error":
                return result
            
            token_data = result["data"]
            user_id = token_data.get("sub")
            
            # Verify user still exists and is active
            user_result = supabase_admin.table('users').select('*').eq('id', user_id).eq('is_active', True).execute()
            
            if not user_result.data:
                return {"status": "error", "message": "User not found or inactive"}
            
            user = user_result.data[0]
            
            # Generate new tokens
            new_token_data = {
                "sub": user["id"], 
                "email": user["email"], 
                "role": user["role"]
            }
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_access_token(data=new_token_data, expires_delta=access_token_expires)
            new_refresh_token = create_refresh_token(data=new_token_data)
            
            return {
                "status": "success",
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "role": user["role"]
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {"status": "error", "message": f"Token refresh failed: {str(e)}"}
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Dict:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: User data or error
        """
        try:
            result = supabase_admin.table('users').select('*').eq('id', user_id).eq('is_active', True).execute()
            
            if not result.data:
                return {"status": "error", "message": "User not found"}
            
            user = result.data[0]
            # Remove sensitive data
            user_response = {k: v for k, v in user.items() if k != 'password_hash'}
            
            return {"status": "success", "user": user_response}
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return {"status": "error", "message": f"Failed to get user: {str(e)}"}
    
    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> Dict:
        """
        Update user information.
        
        Args:
            user_id: User ID
            update_data: Data to update
            
        Returns:
            Dict: Updated user data or error
        """
        try:
            # Prepare update data
            update_dict = update_data.dict(exclude_unset=True)
            if update_dict:
                update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
                
                result = supabase_admin.table('users').update(update_dict).eq('id', user_id).execute()
                
                if not result.data:
                    return {"status": "error", "message": "User not found or update failed"}
                
                user = result.data[0]
                # Remove sensitive data
                user_response = {k: v for k, v in user.items() if k != 'password_hash'}
                
                return {"status": "success", "user": user_response}
            
            return {"status": "error", "message": "No data to update"}
            
        except Exception as e:
            logger.error(f"Update user error: {str(e)}")
            return {"status": "error", "message": f"Failed to update user: {str(e)}"}
    
    @staticmethod
    async def change_password(user_id: str, password_data: PasswordChange) -> Dict:
        """
        Change user password.
        
        Args:
            user_id: User ID
            password_data: Current and new password
            
        Returns:
            Dict: Success or error message
        """
        try:
            # Get current user
            result = supabase_admin.table('users').select('password_hash').eq('id', user_id).execute()
            
            if not result.data:
                return {"status": "error", "message": "User not found"}
            
            user = result.data[0]
            
            # Verify current password
            if not verify_password(password_data.current_password, user['password_hash']):
                return {"status": "error", "message": "Current password is incorrect"}
            
            # Hash new password
            new_password_hash = hash_password(password_data.new_password)
            
            # Update password
            update_result = supabase_admin.table('users').update({
                "password_hash": new_password_hash,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq('id', user_id).execute()
            
            if not update_result.data:
                return {"status": "error", "message": "Failed to update password"}
            
            return {"status": "success", "message": "Password changed successfully"}
            
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            return {"status": "error", "message": f"Failed to change password: {str(e)}"}
    
    @staticmethod
    async def deactivate_user(user_id: str) -> Dict:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: Success or error message
        """
        try:
            result = supabase_admin.table('users').update({
                "is_active": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq('id', user_id).execute()
            
            if not result.data:
                return {"status": "error", "message": "User not found"}
            
            return {"status": "success", "message": "User account deactivated"}
            
        except Exception as e:
            logger.error(f"Deactivate user error: {str(e)}")
            return {"status": "error", "message": f"Failed to deactivate user: {str(e)}"}
    
    @staticmethod
    async def get_all_users(requesting_user_role: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        Get all users (clinicians only).
        
        Args:
            requesting_user_role: Role of the requesting user
            limit: Number of users to return
            offset: Offset for pagination
            
        Returns:
            Dict: List of users or error
        """
        try:
            if requesting_user_role != "clinician":
                return {"status": "error", "message": "Access denied. Clinician role required."}
            
            result = supabase_admin.table('users').select('*').eq('is_active', True).range(offset, offset + limit - 1).execute()
            
            # Remove sensitive data from all users
            users = []
            for user in result.data:
                user_response = {k: v for k, v in user.items() if k != 'password_hash'}
                users.append(user_response)
            
            return {"status": "success", "users": users, "count": len(users)}
            
        except Exception as e:
            logger.error(f"Get all users error: {str(e)}")
            return {"status": "error", "message": f"Failed to get users: {str(e)}"}
    
    @staticmethod
    async def admin_reset_password(email: str, new_password: str) -> Dict:
        """
        Reset user password (admin function).
        
        Args:
            email: User email
            new_password: New password
            
        Returns:
            Dict: Success or error message
        """
        try:
            # Check if user exists
            result = supabase_admin.table('users').select('id, email').eq('email', email).execute()
            
            if not result.data:
                return {"status": "error", "message": "User not found"}
            
            user = result.data[0]
            
            # Hash the new password
            hashed_password = hash_password(new_password)
            
            # Update password
            update_result = supabase_admin.table('users').update({
                "password_hash": hashed_password,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq('id', user['id']).execute()
            
            if not update_result.data:
                return {"status": "error", "message": "Failed to update password"}
            
            logger.info(f"Password reset for user: {email}")
            return {"status": "success", "message": f"Password reset successfully for {email}"}
            
        except Exception as e:
            logger.error(f"Admin reset password error: {str(e)}")
            return {"status": "error", "message": f"Failed to reset password: {str(e)}"}
    
    @staticmethod
    async def request_password_reset(email: str) -> Dict:
        """
        Request a password reset by generating a one-time token and storing its hash.
        Returns a generic success response without revealing if the email exists.
        In development environment, includes the raw token for testing.
        """
        try:
            # Generate secure token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Token validity window
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

            # Attempt to find user to normalize email casing; but do not leak existence
            user_lookup = None
            try:
                user_lookup = supabase_admin.table('users').select('email').eq('email', email).limit(1).execute()
            except Exception:
                user_lookup = None

            target_email = email
            if user_lookup and user_lookup.data:
                target_email = user_lookup.data[0]['email']

            # Store reset record
            supabase_admin.table('password_resets').insert({
                'email': target_email,
                'token_hash': token_hash,
                'expires_at': expires_at.isoformat(),
                'used': False,
            }).execute()

            payload: Dict[str, str] = {"message": "If that email exists, a reset link has been initiated."}
            # In development, return the token to simplify testing
            if os.getenv("ENVIRONMENT", "development").lower() == "development":
                payload["reset_token"] = token
            return {"status": "success", **payload}
        except Exception as e:
            logger.error(f"Request password reset error: {str(e)}")
            return {"status": "error", "message": "Failed to initiate password reset"}

    @staticmethod
    async def confirm_password_reset(token: str, new_password: str) -> Dict:
        """
        Confirm password reset using provided token and set the new password.
        """
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Find valid reset record
            now_iso = datetime.now(timezone.utc).isoformat()
            result = supabase_admin.table('password_resets') \
                .select('id,email,expires_at,used') \
                .eq('token_hash', token_hash) \
                .eq('used', False) \
                .gt('expires_at', now_iso) \
                .order('created_at', desc=True) \
                .limit(1) \
                .execute()

            if not result.data:
                return {"status": "error", "message": "Invalid or expired token"}

            reset_row = result.data[0]
            email = reset_row['email']

            # Get user by email
            user_q = supabase_admin.table('users').select('id,email').eq('email', email).limit(1).execute()
            if not user_q.data:
                return {"status": "error", "message": "User account not found"}

            user = user_q.data[0]

            # Update password
            hashed = hash_password(new_password)
            upd = supabase_admin.table('users').update({
                'password_hash': hashed,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', user['id']).execute()
            if not upd.data:
                return {"status": "error", "message": "Failed to update password"}

            # Mark reset used
            supabase_admin.table('password_resets').update({'used': True}).eq('id', reset_row['id']).execute()

            return {"status": "success", "message": "Password has been reset successfully"}
        except Exception as e:
            logger.error(f"Confirm password reset error: {str(e)}")
            return {"status": "error", "message": "Failed to confirm password reset"}
    
    @staticmethod
    async def cleanup_test_users() -> Dict:
        """
        Remove test users (development function).
        
        Returns:
            Dict: Cleanup result
        """
        try:
            # Define test email patterns
            test_patterns = ['test@example.com', 'clinician@example.com', '%test%', '%@test.%']
            
            deleted_count = 0
            
            # Delete users with test email patterns
            for pattern in test_patterns:
                if '%' in pattern:
                    # Use ilike for pattern matching
                    result = supabase_admin.table('users').delete().ilike('email', pattern).execute()
                else:
                    # Exact match
                    result = supabase_admin.table('users').delete().eq('email', pattern).execute()
                
                if result.data:
                    deleted_count += len(result.data)
            
            logger.info(f"Cleaned up {deleted_count} test users")
            return {"status": "success", "message": f"Cleaned up {deleted_count} test users"}
            
        except Exception as e:
            logger.error(f"Cleanup test users error: {str(e)}")
            return {"status": "error", "message": f"Failed to cleanup test users: {str(e)}"}