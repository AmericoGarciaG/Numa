"""Main FastAPI application for Numa.

This module initializes the FastAPI application and provides the basic
endpoint structure as specified in AGENTS.md.
"""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import security, models, schemas
from app.database import engine, get_db
from app.models import Base
from app.schemas import ChatQuery, ChatResponse
from app.schemas import Transaction as TransactionSchema
from app.services import (create_provisional_transaction_from_audio,
                          get_chat_response, get_user_by_email,
                          verify_transaction_manually,
                          verify_transaction_with_document,
                          create_user, authenticate_user)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Numa AI",
    description="The most intuitive financial assistant that organizes your finances through conversation, without compromising your privacy.",
    version="0.1.0",
)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Decodes token, validates, and returns the current user."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@app.get("/")
def read_root():
    """Root endpoint with welcome message.

    Returns:
        dict: Welcome message as specified in the prompt.
    """
    return {"message": "Welcome to Numa AI"}


@app.post("/users/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registers a new user.
    
    Args:
        user: User creation data with email, name, and password
        db: Database session dependency
        
    Returns:
        User: The newly created user
        
    Raises:
        HTTPException: If email is already registered
    """
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
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
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/transactions/voice", response_model=TransactionSchema, status_code=201)
async def create_transaction_from_voice(
    audio_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a provisional transaction from voice command.

    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz).
    Now protected with JWT authentication.

    Args:
        audio_file: Uploaded audio file containing voice command
        current_user: Current authenticated user from JWT token
        db: Database session dependency

    Returns:
        TransactionSchema: The newly created provisional transaction

    Raises:
        HTTPException: If transaction creation fails
    """
    try:
        # Call service function to create provisional transaction
        transaction = await create_provisional_transaction_from_audio(
            db=db, audio_file=audio_file, user_id=current_user.id
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/transactions/{transaction_id}/verify", response_model=TransactionSchema)
def verify_transaction(
    transaction_id: int, 
    document: UploadFile = File(...), 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a provisional transaction using a source document.

    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).
    Now protected with JWT authentication.

    Args:
        transaction_id: ID of the transaction to verify
        document: Uploaded source document (receipt, invoice, etc.)
        current_user: Current authenticated user from JWT token
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
    transaction_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually verify a provisional transaction without a source document.

    Implements LOGIC.md Rule 2.3 (Creación Verificada Manualmente).
    Now protected with JWT authentication.

    Args:
        transaction_id: ID of the transaction to verify manually
        current_user: Current authenticated user from JWT token
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
async def upload_audio(
    audio_file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alternative endpoint for creating transaction from voice (for USER_GUIDE.md compatibility).
    Now protected with JWT authentication.
    """
    return await create_transaction_from_voice(audio_file=audio_file, current_user=current_user, db=db)


@app.post("/upload-document")
def upload_document(
    transaction_id: int,
    document: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alternative endpoint for verifying transaction with document (for USER_GUIDE.md compatibility).
    Now protected with JWT authentication.
    """
    return verify_transaction(transaction_id=transaction_id, document=document, current_user=current_user, db=db)


@app.post("/chat", response_model=ChatResponse)
def chat_with_numa(
    chat_query: ChatQuery, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat endpoint for conversational queries about expenses.

    Implements LOGIC.md Rules 3.1 and 3.2 (Consultas Básicas de Gastos):
    - Rule 3.1: Consulta de Gasto Total
    - Rule 3.2: Consulta de Gasto por Categoría
    Now protected with JWT authentication.

    Args:
        chat_query: Natural language query from user
        current_user: Current authenticated user from JWT token
        db: Database session dependency

    Returns:
        ChatResponse: Natural language response with expense information

    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Call service function to generate chat response
        response_data = get_chat_response(
            db=db, query=chat_query.message, user_id=current_user.id
        )
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
