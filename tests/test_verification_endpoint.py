"""Test for verification endpoint to verify Rule 2.2 implementation."""

import io

from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def test_verify_transaction_with_document():
    """Test the POST /transactions/{transaction_id}/verify endpoint.

    Verifies Rule 2.2 implementation:
    - Verifies provisional transaction with document
    - Updates transaction with verified data
    - Changes status from provisional to verified
    """
    # Step 1: Create a provisional transaction first (using voice endpoint)
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("test_audio.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )

    assert voice_response.status_code == 201
    provisional_transaction = voice_response.json()
    transaction_id = provisional_transaction["id"]

    # Verify it's provisional
    assert provisional_transaction["status"] == "provisional"
    assert provisional_transaction["amount"] == 120.0
    assert provisional_transaction["concept"] == "la cena"
    assert provisional_transaction["merchant"] is None

    # Step 2: Verify the transaction with a document
    document_content = b"dummy receipt image content"
    document_file = io.BytesIO(document_content)

    verify_response = client.post(
        f"/transactions/{transaction_id}/verify",
        files={"document": ("receipt.jpg", document_file, "image/jpeg")},
    )

    # Verify response
    assert verify_response.status_code == 200

    verified_transaction = verify_response.json()

    # Verify transaction data according to Rule 2.2
    assert verified_transaction["id"] == transaction_id
    assert verified_transaction["status"] == "verified"  # Rule 2.2 Step 4

    # Verify updated data from hardcoded verified_data
    assert verified_transaction["amount"] == 122.50  # Monto Exacto updated
    assert verified_transaction["merchant"] == "La Trattoria"  # Comercio updated
    assert verified_transaction["transaction_date"] is not None  # Fecha updated
    assert verified_transaction["transaction_time"] is not None  # Hora updated

    # Original concept should remain unchanged
    assert verified_transaction["concept"] == "la cena"
    assert verified_transaction["user_id"] == 1

    print("✅ Transaction verification endpoint test passed!")
    print(f"   Transaction ID: {verified_transaction['id']}")
    print(f"   Status: provisional → {verified_transaction['status']}")
    print(f"   Amount: 120.0 → {verified_transaction['amount']}")
    print(f"   Merchant: None → {verified_transaction['merchant']}")
    print(f"   Date: {verified_transaction['transaction_date']}")
    print(f"   Time: {verified_transaction['transaction_time']}")


def test_verify_nonexistent_transaction():
    """Test verification of non-existent transaction returns 404."""
    document_content = b"dummy receipt content"
    document_file = io.BytesIO(document_content)

    response = client.post(
        "/transactions/999/verify",
        files={"document": ("receipt.jpg", document_file, "image/jpeg")},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"

    print("✅ Non-existent transaction test passed!")


if __name__ == "__main__":
    test_verify_transaction_with_document()
    test_verify_nonexistent_transaction()
