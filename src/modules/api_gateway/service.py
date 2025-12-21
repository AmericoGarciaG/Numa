"""API Gateway Service - Business Flow Orchestration (Public Interface).

This module orchestrates business flows by coordinating between
FinanceCore and AIBrain modules.

PROTOCOLO NEXUS: This is the PUBLIC INTERFACE of the APIGateway module.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.modules.ai_brain import service as ai_brain
from src.modules.finance_core import service as finance_core


# ============================================================================
# VOICE TRANSACTION ORCHESTRATION
# ============================================================================

async def orchestrate_voice_transaction(
    db: Session, audio_file: UploadFile, user_id: int
):
    """Orchestrate the voice-to-transaction flow.
    
    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz):
    1. Transcribe audio (AIBrain)
    2. Extract transaction data (AIBrain)
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
    # Step 1: Transcribe audio using AIBrain
    audio_bytes = await audio_file.read()
    transcribed_text = await ai_brain.transcribe_audio(audio_bytes, language="es-MX")
    
    # Step 2: Extract transaction data using AIBrain
    extracted_data = ai_brain.extract_transaction_data(transcribed_text)
    
    # Step 3: Create provisional transaction using FinanceCore
    transaction = finance_core.create_provisional_transaction(
        db=db,
        user_id=user_id,
        amount=extracted_data["amount"],
        concept=extracted_data["concept"]
    )
    
    return transaction


# ============================================================================
# DOCUMENT VERIFICATION ORCHESTRATION
# ============================================================================

async def orchestrate_document_verification(
    db: Session, transaction_id: int, document: UploadFile, user_id: int
):
    """Orchestrate the document verification flow.
    
    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante):
    1. Analyze document (AIBrain)
    2. Classify category (AIBrain)
    3. Verify transaction with document data (FinanceCore)
    
    Args:
        db: Database session
        transaction_id: ID of the transaction to verify
        document: Uploaded document file
        user_id: ID of the user (for security validation)
        
    Returns:
        Transaction: The updated verified transaction
    """
    # Step 1: Analyze document using AIBrain
    document_bytes = await document.read()
    document_data = ai_brain.analyze_document(document_bytes)
    
    # Step 2: Get the transaction to verify ownership
    transaction = db.query(finance_core.Transaction).filter(
        finance_core.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this transaction")
    
    # Step 3: Classify category using AIBrain
    category = ai_brain.classify_category(
        concept=transaction.concept,
        merchant=document_data["vendor"]
    )
    
    # Step 4: Verify transaction using FinanceCore
    verified_transaction = finance_core.verify_transaction_with_document(
        db=db,
        transaction_id=transaction_id,
        amount=document_data["total_amount"],
        merchant=document_data["vendor"],
        transaction_date=document_data["date"],
        category=category
    )
    
    return verified_transaction


# ============================================================================
# MANUAL VERIFICATION ORCHESTRATION
# ============================================================================

async def orchestrate_manual_verification(
    db: Session, transaction_id: int, user_id: int
):
    """Orchestrate the manual verification flow.
    
    Implements LOGIC.MD Rule 2.3 (Creación Verificada Manualmente):
    1. Get transaction and verify ownership
    2. Classify category (AIBrain)
    3. Verify transaction manually (FinanceCore)
    
    Args:
        db: Database session
        transaction_id: ID of the transaction to verify
        user_id: ID of the user (for security validation)
        
    Returns:
        Transaction: The updated verified transaction
    """
    # Step 1: Get the transaction to verify ownership
    transaction = db.query(finance_core.Transaction).filter(
        finance_core.Transaction.id == transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify this transaction")
    
    # Step 2: Classify category using AIBrain (based on concept only)
    category = ai_brain.classify_category(
        concept=transaction.concept,
        merchant=None
    )
    
    # Step 3: Verify transaction manually using FinanceCore
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
    """Handle conversational query about expenses.
    
    Implements LOGIC.md Rules 3.1 and 3.2 (Consultas Básicas de Gastos):
    1. Parse query to detect period and category (AIBrain - future)
    2. Calculate spending using SQL (FinanceCore)
    3. Generate natural language response (AIBrain)
    
    Args:
        db: Database session
        query: Natural language query from user
        user_id: ID of the user making the query
        
    Returns:
        dict: Response data with query, response text, and metadata
    """
    # Step 1: Parse query (simplified - real implementation will use AIBrain)
    query_lower = query.lower()
    
    # Detect time period
    period_keywords = {
        "hoy": ("today", 0),
        "ayer": ("yesterday", 1),
        "semana": ("week", 7),
        "mes": ("month", 30),
        "año": ("year", 365),
    }
    
    detected_period = None
    days_back = 30  # Default to month
    
    for keyword, (period_name, days) in period_keywords.items():
        if keyword in query_lower:
            detected_period = period_name
            days_back = days
            break
    
    # Calculate date range
    end_date = datetime.utcnow()
    if days_back == 0:  # Today
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = end_date - timedelta(days=days_back)
    
    # Detect category
    category_keywords = {
        "alimentación": "Alimentación",
        "comida": "Alimentación",
        "super": "Alimentación",
        "transporte": "Transporte",
        "gasolina": "Transporte",
        "servicios": "Servicios",
        "ocio": "Ocio",
        "entretenimiento": "Ocio",
    }
    
    detected_category = None
    for keyword, category in category_keywords.items():
        if keyword in query_lower:
            detected_category = category
            break
    
    # Step 2: Calculate spending using FinanceCore (SQL-backed)
    total_amount = finance_core.calculate_user_spending(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=detected_category
    )
    
    # Get transaction count
    transactions = finance_core.get_user_transactions(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=detected_category
    )
    transaction_count = len(transactions)
    
    # Step 3: Generate natural language response using AIBrain
    context = {
        "total_amount": total_amount,
        "transaction_count": transaction_count,
        "period": _format_period_text(detected_period, days_back),
        "category": detected_category
    }
    
    response_text = ai_brain.answer_query(query, context)
    
    return {
        "query": query,
        "response": response_text,
        "total_amount": total_amount,
        "period": detected_period,
        "category": detected_category,
        "transaction_count": transaction_count,
    }


def _format_period_text(period: Optional[str], days_back: int) -> str:
    """Format period for natural language response."""
    if period == "today":
        return "hoy"
    elif period == "week":
        return "esta semana"
    elif period == "month":
        return "este mes"
    elif period == "year":
        return "este año"
    else:
        return f"en los últimos {days_back} días"
