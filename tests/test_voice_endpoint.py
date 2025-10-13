"""Basic test for voice endpoint to verify Rule 2.1 implementation."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_transaction_from_voice():
    """Test the POST /transactions/voice endpoint.

    Verifies Rule 2.1 implementation:
    - Creates provisional transaction from voice input
    - Returns transaction with correct status and data
    """
    # Create a dummy audio file for the test
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    # Make request to voice endpoint
    response = client.post(
        "/transactions/voice",
        files={"audio_file": ("test_audio.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )

    # Verify response
    assert response.status_code == 201

    data = response.json()

    # Verify transaction data according to Rule 2.1
    assert data["amount"] == 120.0  # From hardcoded text "gasté 120 pesos"
    assert data["concept"] == "la cena"  # From hardcoded text "en la cena"
    assert data["status"] == "provisional"  # Must be provisional (Rule 2.1 Step 4)
    assert data["user_id"] == 1
    assert "id" in data
    assert "created_at" in data

    print("✅ Voice transaction endpoint test passed!")
    print(f"   Transaction ID: {data['id']}")
    print(f"   Amount: {data['amount']}")
    print(f"   Concept: {data['concept']}")
    print(f"   Status: {data['status']}")


if __name__ == "__main__":
    test_create_transaction_from_voice()
