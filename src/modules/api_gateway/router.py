"""API Gateway Router - HTTP Endpoints.

This module defines all HTTP endpoints for the Numa API.
Endpoints delegate to the orchestration service.
"""

import os
import shutil
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.core import auth, database
from src.modules.api_gateway import service as gateway_service
from src.modules.finance_core import schemas
from src.modules.finance_core import service as finance_service

# Create router
router = APIRouter()

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    """Decodes token, validates, and returns the current user."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = finance_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================


@router.get("/")
def read_root():
    """Root endpoint with welcome message."""
    return {"message": "Welcome to Numa AI - Protocolo Nexus Edition"}


@router.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Registers a new user.

    Args:
        user: User creation data with email, name, and password
        db: Database session dependency

    Returns:
        User: The newly created user

    Raises:
        HTTPException: If email is already registered
    """
    db_user = finance_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return finance_service.create_user(db=db, user=user)


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    """Provides a JWT token for valid user credentials.

    Args:
        form_data: OAuth2 form data with username (email) and password
        db: Database session dependency

    Returns:
        Token: JWT access token with token type

    Raises:
        HTTPException: If credentials are invalid
    """
    user = finance_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ============================================================================
# TRANSACTION ENDPOINTS (Protected)
# ============================================================================


@router.post(
    "/transactions/voice", response_model=list[schemas.Transaction], status_code=201
)
async def create_transaction_from_voice(
    audio_file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Create a provisional transaction from voice command.

    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz).
    Protected with JWT authentication.
    """
    # DEBUG: Save audio locally
    debug_dir = ".debug_audio"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get extension from filename if possible, else default to .webm
    ext = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".webm"
    if not ext:
        ext = ".webm"

    filename = f"debug_{timestamp}_user{current_user.id}{ext}"
    file_path = os.path.join(debug_dir, filename)

    # Reset file pointer to beginning before saving
    await audio_file.seek(0)

    # DEBUG: Check file size
    file_content = await audio_file.read()
    print(f"[DEBUG] Received audio file size: {len(file_content)} bytes")
    await audio_file.seek(0)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    print(f"[DEBUG] Audio saved to: {file_path}")

    # Reset file pointer again so the next service can read it
    await audio_file.seek(0)
    try:
        transactions = await gateway_service.orchestrate_voice_transaction(
            db=db, audio_file=audio_file, user_id=current_user.id
        )
        return transactions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/transactions/{transaction_id}/verify", response_model=schemas.Transaction
)
async def verify_transaction(
    transaction_id: int,
    document: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Verify a provisional transaction using a source document.

    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).
    Protected with JWT authentication.
    """
    transaction = await gateway_service.orchestrate_document_verification(
        db=db, transaction_id=transaction_id, document=document, user_id=current_user.id
    )
    return transaction


@router.post(
    "/transactions/{transaction_id}/verify_manual", response_model=schemas.Transaction
)
async def verify_transaction_manual(
    transaction_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Manually verify a provisional transaction without a source document.

    Implements LOGIC.md Rule 2.3 (Creación Verificada Manualmente).
    Protected with JWT authentication.
    """
    transaction = await gateway_service.orchestrate_manual_verification(
        db=db, transaction_id=transaction_id, user_id=current_user.id
    )
    return transaction


@router.get("/transactions", response_model=list[schemas.Transaction])
def get_transactions(
    current_user=Depends(get_current_user), db: Session = Depends(database.get_db)
):
    """Get all transactions for the current user."""
    return finance_service.get_user_transactions(db=db, user_id=current_user.id)


@router.get("/transactions/daily_summary", response_model=schemas.DailySummary)
def get_daily_summary(
    current_user=Depends(get_current_user), db: Session = Depends(database.get_db)
):
    """Get daily summary for the current user."""
    return finance_service.get_daily_summary(db=db, user_id=current_user.id)


# ============================================================================
# CHAT ENDPOINT (Protected)
# ============================================================================


@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_numa(
    chat_query: schemas.ChatQuery,
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Chat endpoint for conversational queries about expenses.

    Implements LOGIC.md Rules 3.1 and 3.2 (Consultas Básicas de Gastos).
    Protected with JWT authentication.
    """
    try:
        response_data = await gateway_service.handle_chat_query(
            db=db, query=chat_query.message, user_id=current_user.id
        )
        return schemas.ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


# ============================================================================
# ALTERNATIVE ENDPOINTS (for backward compatibility)
# ============================================================================


@router.post("/upload-audio")
async def upload_audio(
    audio_file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Alternative endpoint for creating transaction from voice."""
    return await create_transaction_from_voice(
        audio_file=audio_file, current_user=current_user, db=db
    )


@router.post("/upload-document")
async def upload_document(
    transaction_id: int,
    document: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """Alternative endpoint for verifying transaction with document."""
    return await verify_transaction(
        transaction_id=transaction_id,
        document=document,
        current_user=current_user,
        db=db,
    )
