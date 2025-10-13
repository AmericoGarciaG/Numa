"""Test for chat endpoint to verify Rules 3.1 and 3.2 implementation."""

import io

from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


def setup_test_transactions():
    """Create test transactions to query against."""
    # Create multiple transactions with different categories and amounts
    transactions_created = []

    # Transaction 1: Restaurant - La Trattoria (will be categorized as "Restaurantes")
    audio_content = b"dummy audio content"
    audio_file = io.BytesIO(audio_content)

    voice_response = client.post(
        "/transactions/voice",
        files={"audio_file": ("test_audio.wav", audio_file, "audio/wav")},
        data={"user_id": 1},
    )

    if voice_response.status_code == 201:
        transaction = voice_response.json()

        # Verify it to get it categorized
        document_content = b"dummy receipt content"
        document_file = io.BytesIO(document_content)

        verify_response = client.post(
            f"/transactions/{transaction['id']}/verify",
            files={"document": ("receipt.jpg", document_file, "image/jpeg")},
        )

        if verify_response.status_code == 200:
            transactions_created.append(verify_response.json())

    return transactions_created


def test_rule_31_total_spending_query():
    """Test Rule 3.1: Consulta de Gasto Total.

    Tests natural language queries about total spending in a time period.
    """
    print("💬 Testing Rule 3.1: Total spending queries...")

    # Setup test data
    transactions = setup_test_transactions()

    # Test 1: Query about spending this month
    chat_request = {"message": "¿Cuánto he gastado este mes?", "user_id": 1}

    response = client.post("/chat", json=chat_request)

    assert response.status_code == 200
    data = response.json()

    # Validate Rule 3.1 compliance
    assert "response" in data
    assert "total_amount" in data
    assert "period" in data

    assert data["period"] == "month"
    assert isinstance(data["total_amount"], (int, float))
    assert "este mes" in data["response"]

    print(f"   ✅ Rule 3.1 Test 1 passed!")
    print(f"      Response: {data['response']}")
    print(f"      Total: ${data['total_amount']}")

    # Test 2: Query about spending this week
    chat_request = {"message": "¿Cuánto gasté esta semana?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    assert data["period"] == "week"
    assert "esta semana" in data["response"]

    print(f"   ✅ Rule 3.1 Test 2 passed!")
    print(f"      Weekly spending: ${data['total_amount']}")


def test_rule_32_category_spending_query():
    """Test Rule 3.2: Consulta de Gasto por Categoría.

    Tests natural language queries about spending in specific categories.
    """
    print("💬 Testing Rule 3.2: Category spending queries...")

    # Setup test data
    transactions = setup_test_transactions()

    # Test 1: Query about restaurant spending
    chat_request = {"message": "¿Cuánto he gastado en restaurantes?", "user_id": 1}

    response = client.post("/chat", json=chat_request)

    assert response.status_code == 200
    data = response.json()

    # Validate Rule 3.2 compliance
    assert data["category"] == "Restaurantes"
    assert "restaurantes" in data["response"].lower()
    assert isinstance(data["total_amount"], (int, float))

    print(f"   ✅ Rule 3.2 Test 1 passed!")
    print(f"      Category: {data['category']}")
    print(f"      Response: {data['response']}")
    print(f"      Total: ${data['total_amount']}")

    # Test 2: Query about category + period
    chat_request = {"message": "¿Cuánto gasté en restaurantes esta semana?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    assert data["category"] == "Restaurantes"
    assert data["period"] == "week"
    assert "restaurantes" in data["response"].lower()
    assert "esta semana" in data["response"]

    print(f"   ✅ Rule 3.2 Test 2 passed!")
    print(f"      Category + Period: {data['category']} + {data['period']}")
    print(f"      Response: {data['response']}")


def test_nlp_keyword_detection():
    """Test the NLP simulation keyword detection."""
    print("🧠 Testing NLP keyword detection...")

    # Test different query variations
    test_queries = [
        ("¿Cuánto he gastado hoy?", "today", None),
        ("Gastos de esta semana", "week", None),
        ("¿Cuánto gasté en café?", None, "Café"),
        ("Gastos de supermercado este mes", "month", "Supermercado"),
        ("¿Cuánto en transporte?", None, "Transporte"),
    ]

    for query, expected_period, expected_category in test_queries:
        chat_request = {"message": query, "user_id": 1}

        response = client.post("/chat", json=chat_request)
        data = response.json()

        if expected_period:
            assert (
                data["period"] == expected_period
            ), f"Expected period {expected_period}, got {data['period']}"

        if expected_category:
            assert (
                data["category"] == expected_category
            ), f"Expected category {expected_category}, got {data['category']}"

        print(
            f"   ✅ Query '{query}' correctly detected: period={data['period']}, category={data['category']}"
        )


def test_empty_results_handling():
    """Test handling when no transactions match the query."""
    print("🔍 Testing empty results handling...")

    # Query for a category that likely has no transactions
    chat_request = {"message": "¿Cuánto he gastado en entretenimiento hoy?", "user_id": 1}

    response = client.post("/chat", json=chat_request)
    data = response.json()

    assert response.status_code == 200
    assert data["total_amount"] == 0.0
    assert data["transaction_count"] == 0
    assert "No se encontraron transacciones" in data["response"]

    print(f"   ✅ Empty results handled correctly!")
    print(f"      Response: {data['response']}")


def test_complete_chat_flow():
    """Test complete chat flow demonstrating Rules 3.1 and 3.2."""
    print("🎯 Testing complete conversational flow...")

    # Setup some transactions first
    setup_test_transactions()

    # Simulate a conversation about expenses
    conversation_queries = [
        "¿Cuánto he gastado en total?",
        "¿Y en restaurantes?",
        "¿Cuánto gasté esta semana?",
        "¿Cuánto en café este mes?",
    ]

    conversation_log = []

    for query in conversation_queries:
        chat_request = {"message": query, "user_id": 1}

        response = client.post("/chat", json=chat_request)
        data = response.json()

        conversation_log.append(
            {
                "query": query,
                "response": data["response"],
                "amount": data["total_amount"],
            }
        )

        print(f"   👤 User: {query}")
        print(f"   🤖 Numa: {data['response']}")
        print()

    print("   ✅ Complete conversational flow test passed!")

    return conversation_log


if __name__ == "__main__":
    test_rule_31_total_spending_query()
    test_rule_32_category_spending_query()
    test_nlp_keyword_detection()
    test_empty_results_handling()
    test_complete_chat_flow()
    print("\n🎉 All chat endpoint tests passed!")
