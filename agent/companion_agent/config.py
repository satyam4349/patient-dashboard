"""Configuration settings for the companion agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CompanionConfig:
    """Configuration class for the companion agent."""
    
    def __init__(self):
        # LLM settings
        self.model = "all-MiniLM-L6-v2"  # Default embedding model
        self.temperature = 0.7
        self.max_tokens = 1000
        self.max_retries = 3
        
        # Groq settings
        self.groq_model = "llama-3.1-70b-versatile"
        self.groq_fallback_model = "llama-3.1-8b-instant"
        
        # Memory settings
        self.memory_k = 5  # Number of conversations to remember
        self.summary_trigger_turns = 10  # Number of turns before triggering summary
        self.window_turns = 5  # Number of conversation turns to maintain in context window
        # Idle time before sending a yes/no nudge (in seconds)
        self.yes_no_idle_seconds = 120
        
        # Service settings
        self.default_backend = "groq"
        
        # API Keys (loaded from environment variables)
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")


# Create default config instance
CONFIG = CompanionConfig()

# Also create a dictionary version for backward compatibility
CONFIG_DICT = {
    # LLM settings
    "model": "all-MiniLM-L6-v2",  # Default embedding model
    "temperature": 0.7,
    "max_tokens": 1000,
    
    # Memory settings
    "memory_k": 5,  # Number of conversations to remember
    
    # Service settings
    "default_backend": "groq",
    
    # API Keys (these should be loaded from environment variables)
    "groq_api_key": os.getenv("GROQ_API_KEY"),
    "google_api_key": os.getenv("GOOGLE_API_KEY"),
}
