"""Main FastAPI application for Numa.

This module initializes the FastAPI application and provides the basic
endpoint structure as specified in AGENTS.md.
"""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Base
from app.schemas import ChatQuery, ChatResponse
from app.schemas import Transaction as TransactionSchema
from app.services import (create_provisional_transaction_from_audio,
                          get_chat_response, get_user_by_id,
                          verify_transaction_manually,
                          verify_transaction_with_document)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Numa AI",
    description="The most intuitive financial assistant that organizes your finances through conversation, without compromising your privacy.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Root endpoint with welcome message.

    Returns:
        dict: Welcome message as specified in the prompt.
    """
    return {"message": "Welcome to Numa AI"}


@app.post("/transactions/voice", response_model=TransactionSchema, status_code=201)
def create_transaction_from_voice(
    audio_file: UploadFile = File(...),
    user_id: int = 1,  # Hardcoded for MVP - will be from auth later
    db: Session = Depends(get_db),
):
    """Create a provisional transaction from voice command.

    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz).

    Args:
        audio_file: Uploaded audio file containing voice command
        user_id: ID of the user (hardcoded for MVP)
        db: Database session dependency

    Returns:
        TransactionSchema: The newly created provisional transaction

    Raises:
        HTTPException: If user not found or transaction creation fails
    """
    # Verify user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Call service function to create provisional transaction
        transaction = create_provisional_transaction_from_audio(
            db=db, audio_file=audio_file, user_id=user_id
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/transactions/{transaction_id}/verify", response_model=TransactionSchema)
def verify_transaction(
    transaction_id: int, document: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Verify a provisional transaction using a source document.

    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).

    Args:
        transaction_id: ID of the transaction to verify
        document: Uploaded source document (receipt, invoice, etc.)
        db: Database session dependency

    Returns:
        TransactionSchema: The updated verified transaction

    Raises:
        HTTPException: If transaction not found, not provisional, or verification fails
    """
    # Call service function to verify transaction with document
    transaction = verify_transaction_with_document(
        db=db, transaction_id=transaction_id, document=document
    )
    return transaction


@app.post("/transactions/{transaction_id}/verify_manual", response_model=TransactionSchema)
def verify_transaction_manual(
    transaction_id: int, db: Session = Depends(get_db)
):
    """Manually verify a provisional transaction without a source document.

    Implements LOGIC.md Rule 2.3 (Creación Verificada Manualmente).

    Args:
        transaction_id: ID of the transaction to verify manually
        db: Database session dependency

    Returns:
        TransactionSchema: The updated verified transaction

    Raises:
        HTTPException: If transaction not found, not provisional, or verification fails
    """
    # Call service function to verify transaction manually
    transaction = verify_transaction_manually(db=db, transaction_id=transaction_id)
    return transaction


# Alternative endpoints for user convenience (following USER_GUIDE.md)
@app.post("/upload-audio")
def upload_audio(
    audio_file: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Alternative endpoint for creating transaction from voice (for USER_GUIDE.md compatibility)."""
    return create_transaction_from_voice(audio_file=audio_file, user_id=user_id, db=db)


@app.post("/upload-document")
def upload_document(
    transaction_id: int,
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Alternative endpoint for verifying transaction with document (for USER_GUIDE.md compatibility)."""
    return verify_transaction(transaction_id=transaction_id, document=document, db=db)


@app.post("/chat", response_model=ChatResponse)
def chat_with_numa(chat_query: ChatQuery, db: Session = Depends(get_db)):
    """Chat endpoint for conversational queries about expenses.

    Implements LOGIC.md Rules 3.1 and 3.2 (Consultas Básicas de Gastos):
    - Rule 3.1: Consulta de Gasto Total
    - Rule 3.2: Consulta de Gasto por Categoría

    Args:
        chat_query: Natural language query from user
        db: Database session dependency

    Returns:
        ChatResponse: Natural language response with expense information

    Raises:
        HTTPException: If user not found or query processing fails
    """
    # Verify user exists
    user = get_user_by_id(db, chat_query.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Call service function to generate chat response
        response_data = get_chat_response(
            db=db, query=chat_query.message, user_id=chat_query.user_id
        )
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
