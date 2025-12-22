"""Configuration management for Numa.

This module loads and provides access to environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./numa.db")
    
    # Google Cloud
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "numa-mvp-local")
    GOOGLE_LOCATION: str = os.getenv("GOOGLE_LOCATION", "us-central1")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_for_dev")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "Numa AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


# Global settings instance
settings = Settings()
