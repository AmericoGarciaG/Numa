"""Authentication helpers for tests.

This module provides utilities to handle JWT authentication in tests,
including creating test users and obtaining access tokens.
"""

from typing import Dict
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.services import create_user, get_user_by_email
from app.schemas import UserCreate


def create_test_user_if_not_exists(db: Session, email: str, name: str, password: str) -> User:
    """Create a test user if it doesn't exist, or return existing user.
    
    Args:
        db: Database session
        email: User email
        name: User name
        password: User password
        
    Returns:
        User: The created or existing user
    """
    existing_user = get_user_by_email(db, email=email)
    if existing_user:
        return existing_user
    
    user_data = UserCreate(email=email, name=name, password=password)
    return create_user(db=db, user=user_data)


def get_access_token(client: TestClient, email: str, password: str) -> str:
    """Get access token for a user.
    
    Args:
        client: FastAPI test client
        email: User email
        password: User password
        
    Returns:
        str: JWT access token
        
    Raises:
        AssertionError: If login fails
    """
    login_data = {
        "username": email,  # OAuth2 uses 'username' field for email
        "password": password
    }
    
    response = client.post("/token", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    token_data = response.json()
    return token_data["access_token"]


def get_auth_headers(client: TestClient, email: str = "test@example.com", password: str = "testpass") -> Dict[str, str]:
    """Get authentication headers for a user.
    
    Args:
        client: FastAPI test client
        email: User email (defaults to test user)
        password: User password (defaults to test password)
        
    Returns:
        Dict[str, str]: Headers with Authorization bearer token
    """
    token = get_access_token(client, email, password)
    return {"Authorization": f"Bearer {token}"}


def create_authenticated_user(client: TestClient, db: Session, email: str = "test@example.com", 
                            name: str = "Test User", password: str = "testpass") -> tuple[User, Dict[str, str]]:
    """Create a user and return both user and auth headers.
    
    Args:
        client: FastAPI test client
        db: Database session
        email: User email
        name: User name
        password: User password
        
    Returns:
        tuple[User, Dict[str, str]]: User object and auth headers
    """
    user = create_test_user_if_not_exists(db, email, name, password)
    headers = get_auth_headers(client, email, password)
    return user, headers