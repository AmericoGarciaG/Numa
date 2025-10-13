"""Test chat functionality with real transaction data."""

import io

from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def test_chat_with_real_transactions():
    """Test chat functionality using actual verified transactions."""
    print("🎯 Testing chat with real transaction data...")

    # Step 1: Create and verify multiple transactions
    transactions = []

    # Transaction 1: Restaurant transaction
    print("   📱 Creating restaurant transaction...")
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("dinner.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )

    assert voice_response.status_code == 201
    transaction1 = voice_response.json()

    # Verify transaction 1
    document_content = b"receipt content"
    document_file = io.BytesIO(document_content)

    verify_response = client.post(
        f"/transactions/{transaction1['id']}/verify",
        files={"document": ("receipt1.jpg", document_file, "image/jpeg")},
    )

    assert verify_response.status_code == 200
    verified_transaction1 = verify_response.json()
    transactions.append(verified_transaction1)

    print(
        f"      ✅ Transaction 1 verified: ${verified_transaction1['amount']} at {verified_transaction1['merchant']}"
    )
    print(f"         Category: {verified_transaction1['category']}")

    # Transaction 2: Another restaurant transaction (to test aggregation)
    print("   📱 Creating second transaction...")
    audio_file2 = io.BytesIO(b"dummy audio content 2")

    voice_response2 = client.post(
        "/transactions/voice",
        files={"audio_file": ("lunch.wav", audio_file2, "audio/wav")},
        data={"user_id": 1},
    )

    transaction2 = voice_response2.json()

    # Verify transaction 2
    document_file2 = io.BytesIO(b"receipt content 2")

    verify_response2 = client.post(
        f"/transactions/{transaction2['id']}/verify",
        files={"document": ("receipt2.jpg", document_file2, "image/jpeg")},
    )

    verified_transaction2 = verify_response2.json()
    transactions.append(verified_transaction2)

    print(
        f"      ✅ Transaction 2 verified: ${verified_transaction2['amount']} at {verified_transaction2['merchant']}"
    )

    # Step 2: Test chat queries with real data
    print("   💬 Testing chat queries...")

    # Test 1: Total spending query (Rule 3.1)
    chat_request = {"message": "¿Cuánto he gastado este mes?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    expected_total = sum(t["amount"] for t in transactions)

    print(f"   👤 User: {chat_request['message']}")
    print(f"   🤖 Numa: {data['response']}")

    assert data["total_amount"] == expected_total
    assert data["transaction_count"] == len(transactions)
    assert "$" in data["response"]

    # Test 2: Category spending query (Rule 3.2)
    chat_request = {"message": "¿Cuánto he gastado en restaurantes?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    restaurant_total = sum(
        t["amount"] for t in transactions if t["category"] == "Restaurantes"
    )
    restaurant_count = len([t for t in transactions if t["category"] == "Restaurantes"])

    print(f"   👤 User: {chat_request['message']}")
    print(f"   🤖 Numa: {data['response']}")

    assert data["category"] == "Restaurantes"
    assert data["total_amount"] == restaurant_total
    assert data["transaction_count"] == restaurant_count
    assert "restaurantes" in data["response"].lower()

    # Test 3: Category + Period query (Rule 3.2)
    chat_request = {"message": "¿Cuánto gasté en restaurantes esta semana?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    print(f"   👤 User: {chat_request['message']}")
    print(f"   🤖 Numa: {data['response']}")

    assert data["category"] == "Restaurantes"
    assert data["period"] == "week"
    assert "esta semana" in data["response"]
    assert "restaurantes" in data["response"].lower()

    # Test 4: Non-existent category
    chat_request = {"message": "¿Cuánto gasté en supermercado?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    print(f"   👤 User: {chat_request['message']}")
    print(f"   🤖 Numa: {data['response']}")

    assert data["category"] == "Supermercado"
    assert data["total_amount"] == 0.0
    assert "No se encontraron transacciones" in data["response"]

    print("   ✅ All chat tests with real data passed!")

    # Summary
    print(f"\\n   📊 Test Summary:")
    print(f"      • Total transactions created: {len(transactions)}")
    print(f"      • Total amount: ${expected_total}")
    print(f"      • Restaurant transactions: {restaurant_count}")
    print(f"      • Restaurant total: ${restaurant_total}")
    print(f"      • Chat queries tested: 4")

    return {
        "transactions": transactions,
        "total_amount": expected_total,
        "restaurant_total": restaurant_total,
    }


if __name__ == "__main__":
    result = test_chat_with_real_transactions()
    print(f"\\n🎉 Chat with real data test completed successfully!")
    print(f"   💰 Total processed: ${result['total_amount']}")
    print(f"   🍽️  Restaurant spending: ${result['restaurant_total']}")
