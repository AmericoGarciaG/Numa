"""API Gateway Service - Business Flow Orchestration (Public Interface).

This module orchestrates business flows by coordinating between
FinanceCore and AIBrain modules.

PROTOCOLO NEXUS: This is the PUBLIC INTERFACE of the APIGateway module.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

# Import the new real AI modules
from src.modules.ai_brain import transcriber, reasoning, service as ai_brain_service
# We validly import finance_core
from src.modules.finance_core import service as finance_core


# ============================================================================
# VOICE TRANSACTION ORCHESTRATION
# ============================================================================

async def orchestrate_voice_transaction(
    db: Session, audio_file: UploadFile, user_id: int
):
    """Orchestrate the voice-to-transaction flow.
    
    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz):
    1. Transcribe audio (AIBrain - Google Chirp)
    2. Extract transaction data (AIBrain - Google Gemini)
    3. Create provisional transaction (FinanceCore)
    
    Args:
        db: Database session
        audio_file: Uploaded audio file
        user_id: ID of the user creating the transaction
        
    Returns:
        Transaction: The newly created provisional transaction
        
    Raises:
        ValueError: If transcription or extraction fails
    """
    # Step 1: Transcribe audio using AIBrain (Real Chirp)
    audio_bytes = await audio_file.read()
    
    try:
        transcribed_text = await transcriber.transcribe_audio(audio_bytes, language="es-MX")
        print(f"DEBUG: Transcribed text: {transcribed_text}")
    except Exception as e:
        raise ValueError(f"Transcription failed: {str(e)}")
    
    if not transcribed_text:
        raise ValueError("Audio transcription yielded empty text.")

    # Step 2: Extract transaction data using AIBrain (Real Gemini)
    try:
        extracted_data = reasoning.extract_transaction_data(transcribed_text)
        print(f"DEBUG: Extracted data: {extracted_data}")
    except Exception as e:
        raise ValueError(f"Data extraction failed: {str(e)}")
    
    # Step 3: Create provisional transaction using FinanceCore
    # Ensure amount is float
    try:
        amount = float(extracted_data.get("amount", 0.0))
    except (ValueError, TypeError):
        amount = 0.0

    concept = extracted_data.get("concept", "Gasto sin concepto")
    
    transaction = finance_core.create_provisional_transaction(
        db=db,
        user_id=user_id,
        amount=amount,
        concept=concept
    )
    
    # Note: If Gemini extracted a category, we might want to update it immediately,
    # but the rule says "Provisional". 
    # Logic 2.1 says "Step 3: ... estado PROVISIONAL".
    # Logic 2.3 (Manual) allows category.
    # We could optionally set category if FinanceCore allows updating it on creation or shortly after.
    # FinanceCore `create_provisional_transaction` only takes amount and concept.
    # We will stick to the core interface for now.
    
    return transaction


# ============================================================================
# DOCUMENT VERIFICATION ORCHESTRATION
# ============================================================================

async def orchestrate_document_verification(
    db: Session, transaction_id: int, document: UploadFile, user_id: int
):
    """Orchestrate the document verification flow.
    
    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).
    """
    # Use the placeholder service for now if image analysis not fully implemented in real modules,
    # OR we could implement image analysis in `reasoning.py` too. 
    # For this specific task, "Action 1 & 2" only covered Transcriber and Reasoning (Text).
    # So we keep using the `ai_brain_service` placeholder for document logic 
    # unless we want to upgrade it to real Gemini Vision now.
    # The prompt explicitly asked for 'transcriber.py' and 'reasoning.py' (text).
    # So we will wrap the legacy/placeholder calls for the document parts to avoid breaking.
    
    document_bytes = await document.read()
    document_data = ai_brain_service.analyze_document(document_bytes)
    
    transaction = db.query(finance_core.Transaction).filter(
        finance_core.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this transaction")
    
    category = ai_brain_service.classify_category(
        concept=transaction.concept,
        merchant=document_data.get("vendor")
    )
    
    verified_transaction = finance_core.verify_transaction_with_document(
        db=db,
        transaction_id=transaction_id,
        amount=document_data.get("total_amount", 0.0),
        merchant=document_data.get("vendor", "Unknown"),
        transaction_date=document_data.get("date", datetime.now()),
        category=category
    )
    
    return verified_transaction


# ============================================================================
# MANUAL VERIFICATION ORCHESTRATION
# ============================================================================

async def orchestrate_manual_verification(
    db: Session, transaction_id: int, user_id: int
):
    """Orchestrate the manual verification flow."""
    transaction = db.query(finance_core.Transaction).filter(
        finance_core.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this transaction")
    
    # Use placeholder or simple logic
    category = ai_brain_service.classify_category(
        concept=transaction.concept,
        merchant=None
    )
    
    verified_transaction = finance_core.verify_transaction_manually(
        db=db,
        transaction_id=transaction_id,
        category=category
    )
    
    return verified_transaction


# ============================================================================
# CHAT QUERY ORCHESTRATION
# ============================================================================

async def handle_chat_query(db: Session, query: str, user_id: int) -> dict:
    """Handle conversational query about expenses."""
    # This remains largely similar to the previous implementation 
    # likely using the placeholder `ai_brain.answer_query` for the final text generation,
    # OR we could upgrade it to use `reasoning` if we added a chat method there.
    # Keeping it compatible with existing `api_gateway/service.py` logic structure 
    # but using imports correctly.
    
    # ... (Logic identical to previous file, just import fix) ...
    # For brevity, reusing the core logic from the previous file view 
    # but ensuring we return the dict it expects.
    
    # Re-implementing the simple logic to ensure file consistency:
    query_lower = query.lower()
    
    # Detect period (Simple heuristic)
    detected_period = None
    days_back = 30
    if "hoy" in query_lower:
        detected_period, days_back = "today", 0
    elif "ayer" in query_lower:
        detected_period, days_back = "yesterday", 1
    elif "semana" in query_lower:
        detected_period, days_back = "week", 7
    
    end_date = datetime.utcnow()
    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) if days_back == 0 else end_date - timedelta(days=days_back)

    # Detect category (Simple heuristic)
    detected_category = None
    if "comida" in query_lower or "super" in query_lower:
        detected_category = "Alimentación"
    elif "gasolina" in query_lower or "uber" in query_lower:
        detected_category = "Transporte"

    total_amount = finance_core.calculate_user_spending(
        db=db, user_id=user_id, start_date=start_date, end_date=end_date, category=detected_category
    )
    
    transactions = finance_core.get_user_transactions(
        db=db, user_id=user_id, start_date=start_date, end_date=end_date, category=detected_category
    )
    
    context = {
        "total_amount": total_amount,
        "transaction_count": len(transactions),
        "period": detected_period,
        "category": detected_category
    }
    
    # Keep using the placeholder for the chat response generation for now, 
    # as the task focused on "Voice Transaction" flow.
    response_text = ai_brain_service.answer_query(query, context)
    
    return {
        "query": query,
        "response": response_text,
        "total_amount": total_amount,
        "period": detected_period,
        "category": detected_category,
        "transaction_count": len(transactions),
    }
