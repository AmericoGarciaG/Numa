"""Configuration management for Numa.

This module loads and provides access to environment variables and application settings.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file
load_dotenv()

# Auto-detect credentials.json for local development
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    # Look for credentials.json in project root (2 levels up from src/core)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    creds_path = os.path.join(root_dir, "credentials.json")
    if os.path.exists(creds_path):
        print(f"Auto-loading credentials from: {creds_path}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    else:
        print(
            "⚠️ Warning: credentials.json not found in root and GOOGLE_APPLICATION_CREDENTIALS not set."
        )


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./numa.db")

    # Google Cloud
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "numa-mvp-local")
    GOOGLE_LOCATION: str = os.getenv("GOOGLE_LOCATION", "us-central1")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", ""
    )

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
