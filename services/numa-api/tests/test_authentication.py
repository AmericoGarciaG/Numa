"""Tests for authentication system (OAuth2 + JWT)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import create_test_user_if_not_exists

client = TestClient(app)


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user(self, test_db_session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@test.com",
            "name": "New User",
            "password": "newpassword123"
        }
        
        response = client.post("/users/", json=user_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["email"] == user_data["email"]
        assert result["name"] == user_data["name"]
        assert "id" in result
        assert "hashed_password" not in result  # Password should not be returned
        
    def test_register_duplicate_email(self, test_db_session):
        """Test that registering with existing email fails."""
        # First user
        user_data = {
            "email": "duplicate@test.com",
            "name": "First User", 
            "password": "password1"
        }
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == 200
        
        # Second user with same email
        user_data2 = {
            "email": "duplicate@test.com",
            "name": "Second User",
            "password": "password2" 
        }
        response2 = client.post("/users/", json=user_data2)
        
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]


class TestUserLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials(self, test_db_session):
        """Test login with valid credentials."""
        # Create test user
        create_test_user_if_not_exists(
            test_db_session, 
            "login@test.com", 
            "Login User", 
            "loginpass"
        )
        
        login_data = {
            "username": "login@test.com",
            "password": "loginpass"
        }
        
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 200
        result = response.json()
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert len(result["access_token"]) > 20  # JWT should be long
        
    def test_login_invalid_email(self, test_db_session):
        """Test login with non-existent email."""
        login_data = {
            "username": "nonexistent@test.com", 
            "password": "anypassword"
        }
        
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
        
    def test_login_invalid_password(self, test_db_session):
        """Test login with wrong password."""
        # Create test user
        create_test_user_if_not_exists(
            test_db_session,
            "wrongpass@test.com",
            "Wrong Pass User", 
            "correctpass"
        )
        
        login_data = {
            "username": "wrongpass@test.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/token", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]


class TestProtectedEndpoints:
    """Test that endpoints require authentication."""
    
    def test_protected_endpoint_without_token(self):
        """Test that protected endpoints require authentication."""
        # Test voice endpoint
        response = client.post("/transactions/voice", files={"audio_file": ("test.wav", b"fake audio", "audio/wav")})
        assert response.status_code == 401
        
        # Test chat endpoint  
        response = client.post("/chat", json={"message": "test message"})
        assert response.status_code == 401
        
    def test_protected_endpoint_with_invalid_token(self):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.post("/chat", json={"message": "test"}, headers=headers)
        assert response.status_code == 401
        
    def test_protected_endpoint_with_valid_token(self, test_db_session):
        """Test that valid tokens allow access."""
        # Create user and get token
        create_test_user_if_not_exists(
            test_db_session,
            "protected@test.com", 
            "Protected User",
            "protectedpass"
        )
        
        # Get token
        login_data = {
            "username": "protected@test.com",
            "password": "protectedpass"
        }
        token_response = client.post("/token", data=login_data)
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]
        
        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/chat", json={"message": "¿Cuánto gasté?"}, headers=headers)
        
        assert response.status_code == 200
        assert "response" in response.json()