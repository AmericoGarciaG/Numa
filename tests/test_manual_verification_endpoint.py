"""Integration tests for manual verification endpoint (Rule 2.3).

Tests the complete API flow for manually verifying provisional transactions
without requiring source documents.
"""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_manual_verification_endpoint_success():
    """Test successful manual verification of a provisional transaction.
    
    This test validates the integration of:
    - Rule 2.1: Voice command creates provisional transaction
    - Rule 2.3: Manual verification without document
    - Rule 2.4: Auto-categorization is applied
    """
    print("🚀 Starting integration test: Manual Verification Endpoint")
    
    # STEP 1: Create provisional transaction via voice (Rule 2.1)
    print("📢 Step 1: Creating provisional transaction from voice command...")
    
    audio_content = b"dummy audio content representing: gaste 75 pesos en la cena"
    audio_file = io.BytesIO(audio_content)
    
    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("dinner_expense.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )
    
    assert voice_response.status_code == 201
    provisional_transaction = voice_response.json()
    
    print(f"   ✅ Provisional transaction created:")
    print(f"      ID: {provisional_transaction['id']}")
    print(f"      Status: {provisional_transaction['status']}")
    print(f"      Amount: {provisional_transaction['amount']}")
    print(f"      Concept: {provisional_transaction['concept']}")
    
    # Validate initial provisional state (Rule 2.1 compliance)
    assert provisional_transaction["status"] == "provisional"
    assert provisional_transaction["amount"] == 120.0  # Default from simulation
    assert provisional_transaction["concept"] == "la cena"  # Default from simulation
    assert provisional_transaction["merchant"] is None
    assert provisional_transaction["transaction_date"] is None
    assert provisional_transaction["category"] is None  # No category yet
    
    transaction_id = provisional_transaction["id"]
    
    # STEP 2: Manually verify transaction (Rule 2.3)
    print("✋ Step 2: Manually verifying transaction without document...")
    
    verify_response = client.post(f"/transactions/{transaction_id}/verify_manual")
    
    assert verify_response.status_code == 200
    verified_transaction = verify_response.json()
    
    print(f"   ✅ Transaction manually verified:")
    print(f"      ID: {verified_transaction['id']} (unchanged)")
    print(f"      Status: provisional → {verified_transaction['status']}")
    print(f"      Amount: {verified_transaction['amount']} (unchanged)")
    print(f"      Concept: {verified_transaction['concept']} (unchanged)")
    print(f"      Merchant: {verified_transaction['merchant']} (still None)")
    print(f"      Category: {verified_transaction['category']} (auto-assigned)")
    
    # Validate Rule 2.3 compliance
    assert verified_transaction["id"] == transaction_id  # Same transaction
    assert verified_transaction["status"] == "verified_manual"  # Status changed to verified_manual
    assert verified_transaction["amount"] == 120.0  # Amount unchanged (no document data)
    assert verified_transaction["concept"] == "la cena"  # Original concept preserved
    assert verified_transaction["merchant"] is None  # No merchant (no document)
    assert verified_transaction["transaction_date"] is None  # No date (no document)
    assert verified_transaction["transaction_time"] is None  # No time (no document)
    assert verified_transaction["user_id"] == 1  # User unchanged
    
    # Validate Rule 2.4 compliance (Auto-categorization based on concept)
    assert verified_transaction["category"] == "Restaurantes"  # "cena" → "Restaurantes"
    
    # STEP 3: Validate complete manual verification flow
    print("🔍 Step 3: Validating manual verification flow compliance...")
    
    # Original voice data should be preserved
    original_voice_data = {
        "concept": "la cena",
        "amount": 120.0,
        "user_id": 1
    }
    
    for key, value in original_voice_data.items():
        assert verified_transaction[key] == value
    
    # Manual verification specific validations
    manual_verification_data = {
        "status": "verified_manual",
        "merchant": None,  # No merchant data from manual verification
        "transaction_date": None,  # No document date
        "transaction_time": None,  # No document time
        "category": "Restaurantes"  # Auto-categorized based on concept
    }
    
    for key, value in manual_verification_data.items():
        assert verified_transaction[key] == value
    
    print("   ✅ Manual verification flow validation passed!")
    
    print("🎉 Integration test completed successfully!")
    print("   📋 Summary:")
    print(f"      • Voice command processed (Rule 2.1) ✅")
    print(f"      • Manual verification completed (Rule 2.3) ✅")
    print(f"      • Auto-categorization applied (Rule 2.4) ✅")
    print(f"      • Transaction state: provisional → verified_manual ✅")
    print(f"      • Original data preserved ✅")
    print(f"      • Category assigned: {verified_transaction['category']} ✅")
    
    return verified_transaction


def test_manual_verification_endpoint_not_found():
    """Test manual verification fails with 404 for non-existent transaction."""
    print("🔍 Testing manual verification with non-existent transaction...")
    
    response = client.post("/transactions/999/verify_manual")
    
    assert response.status_code == 404
    error_data = response.json()
    assert "Transaction not found" in error_data["detail"]
    
    print("   ✅ Correctly returned 404 for non-existent transaction")


def test_manual_verification_endpoint_already_verified():
    """Test manual verification fails with 400 for already verified transaction."""
    print("🔍 Testing manual verification with already verified transaction...")
    
    # STEP 1: Create provisional transaction
    audio_content = b"dummy audio content representing: gaste 50 pesos en cafe"
    audio_file = io.BytesIO(audio_content)
    
    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("coffee_expense.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )
    
    assert voice_response.status_code == 201
    transaction_id = voice_response.json()["id"]
    
    # STEP 2: Verify transaction with document first
    receipt_content = b"dummy receipt image"
    receipt_file = io.BytesIO(receipt_content)
    
    verify_response = client.post(
        f"/transactions/{transaction_id}/verify",
        files={"document": ("receipt.jpg", receipt_file, "image/jpeg")},
    )
    
    assert verify_response.status_code == 200
    assert verify_response.json()["status"] == "verified"
    
    # STEP 3: Try to manually verify already verified transaction
    manual_verify_response = client.post(f"/transactions/{transaction_id}/verify_manual")
    
    assert manual_verify_response.status_code == 400
    error_data = manual_verify_response.json()
    assert "not in provisional state" in error_data["detail"]
    
    print("   ✅ Correctly returned 400 for already verified transaction")


def test_manual_verification_endpoint_already_manually_verified():
    """Test manual verification fails with 400 for already manually verified transaction."""
    print("🔍 Testing manual verification with already manually verified transaction...")
    
    # STEP 1: Create provisional transaction
    audio_content = b"dummy audio content representing: gaste 30 pesos en transporte"
    audio_file = io.BytesIO(audio_content)
    
    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("transport_expense.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )
    
    assert voice_response.status_code == 201
    transaction_id = voice_response.json()["id"]
    
    # STEP 2: Manually verify transaction first time
    first_verify_response = client.post(f"/transactions/{transaction_id}/verify_manual")
    
    assert first_verify_response.status_code == 200
    assert first_verify_response.json()["status"] == "verified_manual"
    
    # STEP 3: Try to manually verify again
    second_verify_response = client.post(f"/transactions/{transaction_id}/verify_manual")
    
    assert second_verify_response.status_code == 400
    error_data = second_verify_response.json()
    assert "not in provisional state" in error_data["detail"]
    
    print("   ✅ Correctly returned 400 for already manually verified transaction")


if __name__ == "__main__":
    test_manual_verification_endpoint_success()
    test_manual_verification_endpoint_not_found()
    test_manual_verification_endpoint_already_verified()
    test_manual_verification_endpoint_already_manually_verified()
    print("🎉 All manual verification endpoint tests passed!")