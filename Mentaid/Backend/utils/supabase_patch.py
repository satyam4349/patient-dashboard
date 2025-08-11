"""
Supabase realtime import patch.

This module patches the realtime import issue in supabase-py when realtime features
are not needed. It should be imported before any supabase imports.

Issue: ModuleNotFoundError: No module named 'websockets.asyncio'
Solution: Mock the realtime module since we only use database and auth features.
"""
import sys
import logging
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

def patch_supabase_realtime():
    """
    Patch the supabase realtime import to avoid websockets.asyncio dependency.
    
    This is safe when you only use:
    - Database operations (table, select, insert, update, delete)
    - Authentication (create_client, auth operations)
    
    This should NOT be used if you need:
    - Real-time subscriptions
    - Live queries
    - WebSocket connections
    """
    try:
        # Check if realtime is already imported
        if 'realtime' in sys.modules:
            logger.info("Realtime module already exists, skipping patch")
            return
        
        # Create mock realtime module
        mock_realtime = MagicMock()
        
        # Mock the specific classes that supabase tries to import
        mock_realtime.AuthorizationError = Exception
        mock_realtime.NotConnectedError = Exception
        
        # Add the mock to sys.modules
        sys.modules['realtime'] = mock_realtime
        
        logger.info("Successfully patched supabase realtime import")
        
    except Exception as e:
        logger.error(f"Failed to patch supabase realtime: {e}")
        raise

# Apply the patch when this module is imported
patch_supabase_realtime()