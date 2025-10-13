"""Test for voice endpoint with JWT authentication."""

import io

from fastapi.testclient import TestClient

from app.main import app
from tests.auth_helpers import create_authenticated_user

client = TestClient(app)


def test_create_transaction_from_voice(test_db_session):
    """Test the POST /transactions/voice endpoint with authentication.

    Verifies Rule 2.1 implementation with JWT authentication:
    - Creates provisional transaction from voice input
    - Returns transaction with correct status and data
    - Requires valid JWT token
    """
    # Create authenticated user
    user, headers = create_authenticated_user(
        client, test_db_session, "voice@test.com", "Voice User", "voicepass"
    )
    
    # Create a dummy audio file for the test
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    # Make request to voice endpoint with authentication
    response = client.post(
        "/transactions/voice",
        files={"audio_file": ("test_audio.wav", audio_file, "audio/wav")},
        headers=headers,
    )

    # Verify response
    assert response.status_code == 201

    data = response.json()

    # Verify transaction data according to Rule 2.1
    assert data["amount"] == 120.0  # From hardcoded text "gasté 120 pesos"
    assert data["concept"] == "la cena"  # From hardcoded text "en la cena"
    assert data["status"] == "provisional"  # Must be provisional (Rule 2.1 Step 4)
    assert data["user_id"] == user.id  # Now comes from authenticated user
    assert "id" in data
    assert "created_at" in data

    print("✅ Voice transaction endpoint test passed!")
    print(f"   Transaction ID: {data['id']}")
    print(f"   Amount: {data['amount']}")
    print(f"   Concept: {data['concept']}")
    print(f"   Status: {data['status']}")
    

def test_voice_endpoint_requires_authentication():
    """Test that voice endpoint requires authentication."""
    # Create a dummy audio file
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    # Make request without authentication
    response = client.post(
        "/transactions/voice",
        files={"audio_file": ("test_audio.wav", audio_file, "audio/wav")},
    )

    # Should require authentication
    assert response.status_code == 401
