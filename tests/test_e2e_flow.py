"""End-to-end test for the complete voice → verification flow (Rules 2.1 → 2.2)."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_complete_voice_to_verification_flow():
    """Test complete flow: voice command creates provisional, then gets verified with document.

    This test validates the integration of:
    - Rule 2.1: Creación Provisional por Voz
    - Rule 2.2: Verificación por Comprobante
    """
    print("🚀 Starting end-to-end test: Voice → Verification flow")

    # STEP 1: Create provisional transaction via voice (Rule 2.1)
    print("📢 Step 1: Creating provisional transaction from voice command...")

    audio_content = b"dummy audio content representing: gaste 120 pesos en la cena"
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
    print(f"      Merchant: {provisional_transaction['merchant']}")

    # Validate Rule 2.1 compliance
    assert provisional_transaction["status"] == "provisional"
    assert provisional_transaction["amount"] == 120.0
    assert provisional_transaction["concept"] == "la cena"
    assert provisional_transaction["merchant"] is None
    assert provisional_transaction["transaction_date"] is None

    transaction_id = provisional_transaction["id"]

    # STEP 2: Verify transaction with document (Rule 2.2)
    print("🧾 Step 2: Verifying transaction with receipt document...")

    receipt_content = (
        b"dummy receipt image showing: La Trattoria, $122.50, today's date"
    )
    receipt_file = io.BytesIO(receipt_content)

    verify_response = client.post(
        f"/transactions/{transaction_id}/verify",
        files={"document": ("receipt_la_trattoria.jpg", receipt_file, "image/jpeg")},
    )

    assert verify_response.status_code == 200
    verified_transaction = verify_response.json()

    print(f"   ✅ Transaction verified:")
    print(f"      ID: {verified_transaction['id']} (unchanged)")
    print(f"      Status: provisional → {verified_transaction['status']}")
    print(f"      Amount: 120.0 → {verified_transaction['amount']}")
    print(f"      Concept: {verified_transaction['concept']} (unchanged)")
    print(f"      Merchant: None → {verified_transaction['merchant']}")
    print(f"      Date: {verified_transaction['transaction_date']}")
    print(f"      Time: {verified_transaction['transaction_time']}")

    # Validate Rule 2.2 compliance
    assert verified_transaction["id"] == transaction_id  # Same transaction
    assert verified_transaction["status"] == "verified"  # Status changed
    assert verified_transaction["amount"] == 122.50  # Amount updated with precise value
    assert verified_transaction["concept"] == "la cena"  # Original concept preserved
    assert verified_transaction["merchant"] == "La Trattoria"  # Merchant extracted
    assert verified_transaction["transaction_date"] is not None  # Date added
    assert verified_transaction["transaction_time"] is not None  # Time added
    assert verified_transaction["user_id"] == 1  # User unchanged

    # Validate Rule 2.4 compliance (Auto-categorization)
    assert verified_transaction["category"] == "Restaurantes"  # Auto-categorized

    # STEP 3: Validate complete flow
    print("🔍 Step 3: Validating complete flow compliance...")

    # The transaction should have evolved from provisional to verified
    # with enhanced data while preserving original voice-extracted concept
    original_voice_data = {"concept": "la cena", "user_id": 1}

    document_verified_data = {
        "amount": 122.50,
        "merchant": "La Trattoria",
        "status": "verified",
    }

    # Original voice data should be preserved
    for key, value in original_voice_data.items():
        assert verified_transaction[key] == value

    # Document data should be added/updated
    for key, value in document_verified_data.items():
        assert verified_transaction[key] == value

    print("   ✅ Flow validation passed!")

    print("🎉 End-to-end test completed successfully!")
    print("   📋 Summary:")
    print(f"      • Voice command processed (Rule 2.1) ✅")
    print(f"      • Document verification completed (Rule 2.2) ✅")
    print(f"      • Auto-categorization applied (Rule 2.4) ✅")
    print(f"      • Transaction state: provisional → verified ✅")
    print(f"      • Category assigned: {verified_transaction['category']} ✅")
    print(f"      • Data integrity maintained ✅")

    return verified_transaction


if __name__ == "__main__":
    test_complete_voice_to_verification_flow()
