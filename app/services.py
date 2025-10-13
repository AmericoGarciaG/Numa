"""Business logic services for Numa.

This module contains the core application logic as specified in LOGIC.md.
API endpoints should be lean and delegate to these service functions.
"""

import re

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.models import Transaction, TransactionStatus, User
from app.schemas import Transaction as TransactionSchema
from app.simulations import (
    DEFAULT_VOICE_TRANSCRIPTION,
    DEFAULT_VERIFICATION_DATA,
    CATEGORY_MAP,
    CONCEPT_KEYWORDS,
    DEFAULT_CATEGORY,
    CHAT_CATEGORY_KEYWORDS,
    SIMULATION_MESSAGES,
)


def create_provisional_transaction_from_audio(
    db: Session, audio_file: UploadFile, user_id: int
) -> Transaction:
    """Create a provisional transaction from voice command.

    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz):
    - Input: Un comando de voz del User describiendo un gasto o ingreso
    - Action:
      1. El sistema debe transcribir el audio a texto
      2. Un LLM debe extraer del texto las entidades mínimas: Monto y Concepto
      3. Se debe crear una Transaction con el Monto y Concepto extraídos
      4. La Transaction debe tener el estado provisional
      5. El sistema debe confirmar verbalmente y por texto al usuario
    - Output: Una nueva Transaction en estado provisional

    Args:
        db: Database session
        audio_file: Uploaded audio file (currently ignored for simulation)
        user_id: ID of the user creating the transaction

    Returns:
        Transaction: The newly created provisional transaction

    Raises:
        ValueError: If amount or concept cannot be extracted from audio
    """
    # Step 1: Simulate audio transcription (Rule 2.1 - Step 1)
    # For now, ignore audio_file content and use hardcoded text as specified
    transcribed_text = DEFAULT_VOICE_TRANSCRIPTION

    # Step 2: Simulate LLM extraction of minimal entities (Rule 2.1 - Step 2)
    amount, concept = _extract_amount_and_concept_from_text(transcribed_text)

    # Step 3: Create Transaction with extracted data (Rule 2.1 - Step 3)
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        concept=concept,
        status=TransactionStatus.PROVISIONAL,  # Rule 2.1 - Step 4: Must be provisional
    )

    # Save to database
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Step 5: Confirmation will be handled by the endpoint response

    return transaction


def _extract_amount_and_concept_from_text(text: str) -> tuple[float, str]:
    """Extract amount and concept from transcribed text.

    This simulates LLM extraction as specified in Rule 2.1 Step 2.
    Uses simple regex patterns for the simulation.

    Args:
        text: Transcribed audio text

    Returns:
        tuple: (amount, concept) extracted from text

    Raises:
        ValueError: If amount or concept cannot be extracted
    """
    # Extract amount using regex - look for numbers followed by "pesos"
    amount_pattern = r"(\d+(?:\.\d+)?)\s*pesos"
    amount_match = re.search(amount_pattern, text.lower())

    if not amount_match:
        raise ValueError("Could not extract amount from audio text")

    amount = float(amount_match.group(1))

    # Extract concept - look for text after "en"
    concept_pattern = r"en\s+(.+?)(?:\s*$|\.)"
    concept_match = re.search(concept_pattern, text.lower())

    if not concept_match:
        # Fallback: extract text after common spending verbs
        fallback_pattern = (
            r"(?:gasté|compré|pagué).*?(?:pesos?)?\s*(?:en\s+)?(.+?)(?:\s*$|\.)"
        )
        fallback_match = re.search(fallback_pattern, text.lower())

        if not fallback_match:
            raise ValueError("Could not extract concept from audio text")

        concept = fallback_match.group(1).strip()
    else:
        concept = concept_match.group(1).strip()

    return amount, concept


def verify_transaction_with_document(
    db: Session, transaction_id: int, document: UploadFile
) -> Transaction:
    """Verify a provisional transaction using a source document.

    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante):
    - Input: Un SourceDocument (ej. una imagen de un recibo) asociado a una Transaction provisional
    - Action:
      1. Un LLM multimodal debe analizar el SourceDocument
      2. El LLM debe extraer los datos detallados: Monto Exacto, Comercio, Fecha, Hora
      3. El sistema debe actualizar la Transaction existente con esta información precisa
      4. El estado de la Transaction debe cambiar de provisional a verified
      5. El SourceDocument debe quedar vinculado a la Transaction
    - Output: Una Transaction actualizada en estado verified

    Args:
        db: Database session
        transaction_id: ID of the transaction to verify
        document: Uploaded source document (receipt, invoice, etc.)

    Returns:
        Transaction: The updated verified transaction

    Raises:
        HTTPException: If transaction not found or not in provisional state
    """
    from datetime import datetime

    from fastapi import HTTPException

    # Step 1: Find the Transaction by transaction_id (Rule 2.2 prerequisite)
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Verify transaction is in provisional state (logical requirement)
    if transaction.status != TransactionStatus.PROVISIONAL:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is not in provisional state. Current state: {transaction.status.value}",
        )

    # Step 2: Simulate LLM multimodal analysis of SourceDocument (Rule 2.2 - Step 1)
    # For now, ignore document content and use hardcoded verified data as specified
    verified_data = DEFAULT_VERIFICATION_DATA.copy()

    # Step 3: Update Transaction with precise information (Rule 2.2 - Step 3)
    transaction.amount = verified_data["amount"]  # Monto Exacto
    transaction.merchant = verified_data["vendor"]  # Comercio
    transaction.transaction_date = verified_data["transaction_date"]  # Fecha
    transaction.transaction_time = verified_data["transaction_date"].strftime(
        "%H:%M:%S"
    )  # Hora

    # Step 4: Change status from provisional to verified (Rule 2.2 - Step 4)
    transaction.status = TransactionStatus.VERIFIED

    # Step 5: Auto-categorize transaction (Rule 2.4 integration)
    # This triggers after transaction reaches verified state
    transaction = _auto_categorize_transaction(transaction)

    # Step 6: SourceDocument linkage will be implemented in a future prompt
    # For now, we focus on the core transaction verification logic

    # Save changes to database
    db.commit()
    db.refresh(transaction)

    return transaction


def verify_transaction_manually(db: Session, transaction_id: int) -> Transaction:
    """Verify a provisional transaction manually without a source document.

    Implements LOGIC.md Rule 2.3 (Creación Verificada Manualmente):
    - Input: Un transaction_id de una Transaction en estado provisional
    - Action:
      1. El User confirma manualmente que la Transaction es correcta sin necesidad de comprobante
      2. El sistema cambia el estado de provisional a verified_manual
      3. Se aplica auto-categorización basada en el Concepto original
    - Output: Una Transaction actualizada en estado verified_manual con categoría asignada

    Args:
        db: Database session
        transaction_id: ID of the transaction to verify manually

    Returns:
        Transaction: The updated verified transaction

    Raises:
        HTTPException: If transaction not found or not in provisional state
    """
    from fastapi import HTTPException

    # Step 1: Find the Transaction by transaction_id (Rule 2.3 prerequisite)
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Step 2: Verify transaction is in provisional state (logical requirement)
    if transaction.status != TransactionStatus.PROVISIONAL:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is not in provisional state. Current state: {transaction.status.value}",
        )

    # Step 3: Change status from provisional to verified_manual (Rule 2.3 - Step 2)
    transaction.status = TransactionStatus.VERIFIED_MANUAL

    # Step 4: Auto-categorize transaction based on concept (Rule 2.3 - Step 3)
    # This applies Rule 2.4 integration, using the original concept for categorization
    transaction = _auto_categorize_transaction(transaction)

    # Step 5: Save changes to database
    db.commit()
    db.refresh(transaction)

    return transaction


def _auto_categorize_transaction(transaction: Transaction) -> Transaction:
    """Automatically categorize a transaction based on merchant.

    Implements LOGIC.md Rule 2.4 (Categorización Automática):
    - Trigger: Después de que una Transaction alcanza el estado verified o verified_manual
    - Action:
      1. El sistema debe usar un LLM para analizar el Comercio y el Concepto de la Transaction
      2. Basándose en el historial de categorización del User y en el conocimiento general,
         el LLM debe asignar una categoría
      3. Si es un comercio nuevo, la categoría sugerida debe ser presentada al User
         para confirmación la primera vez
    - Output: La Transaction actualizada con un campo category

    Args:
        transaction: Transaction object to categorize

    Returns:
        Transaction: The same transaction object with category assigned
    """
    # Step 1: Simulate LLM analysis of Comercio and Concepto (Rule 2.4 - Step 1)
    # For now, use a simple dictionary mapping of known merchants to categories
    category_map = CATEGORY_MAP

    # Step 2: Assign category based on merchant (Rule 2.4 - Step 2)
    if transaction.merchant and transaction.merchant in category_map:
        transaction.category = category_map[transaction.merchant]
    else:
        # For unknown merchants, use a fallback category or analyze concept
        # This simulates LLM general knowledge categorization
        concept_keywords = CONCEPT_KEYWORDS

        # Analyze concept for category hints
        if transaction.concept:
            concept_lower = transaction.concept.lower()
            for keyword, category in concept_keywords.items():
                if keyword in concept_lower:
                    transaction.category = category
                    break
            else:
                # Default category for unknown cases
                transaction.category = DEFAULT_CATEGORY
        else:
            transaction.category = DEFAULT_CATEGORY

    # Step 3: For MVP, we automatically assign the category
    # In a real implementation, new merchants would trigger user confirmation

    return transaction


def get_chat_response(db: Session, query: str, user_id: int = 1) -> dict:
    """Generate a conversational response to user queries about expenses.

    Implements LOGIC.md Rules 3.1 and 3.2 (Consultas Básicas de Gastos):

    Rule 3.1 (Consulta de Gasto Total):
    - Input: Una pregunta del User en lenguaje natural sobre sus gastos totales
             en un período de tiempo
    - Action:
      1. El sistema debe interpretar la pregunta para identificar el período de tiempo
      2. Debe buscar todas las Transactions de tipo "gasto" para ese User dentro del período
      3. Debe sumar los Montos de las transacciones encontradas
    - Output: Una respuesta en lenguaje natural indicando el monto total gastado

    Rule 3.2 (Consulta de Gasto por Categoría):
    - Input: Una pregunta del User sobre sus gastos en una categoría específica
    - Action:
      1. El sistema debe interpretar la pregunta para identificar el período y la categoría
      2. Debe buscar todas las Transactions que coincidan con la categoría y período
      3. Debe sumar los Montos
    - Output: Una respuesta en lenguaje natural con el monto total de la categoría

    Args:
        db: Database session
        query: Natural language query from user
        user_id: ID of the user making the query

    Returns:
        dict: Response data with query, response text, and metadata
    """
    from datetime import datetime, timedelta

    from sqlalchemy import and_, func

    query_lower = query.lower()

    # Step 1: Simulate NLP interpretation for time period (Rules 3.1 & 3.2 - Step 1)
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

    # Calculate date range - use UTC to match database timestamps
    end_date = datetime.utcnow()
    if days_back == 0:  # Today
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = end_date - timedelta(days=days_back)

    # Step 2: Simulate NLP interpretation for category (Rule 3.2 - Step 1)
    category_keywords = CHAT_CATEGORY_KEYWORDS

    detected_category = None
    for keyword, category in category_keywords.items():
        if keyword in query_lower:
            detected_category = category
            break

    # Step 3: Build SQLAlchemy query based on detected parameters
    query_builder = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.status.in_(
                [TransactionStatus.VERIFIED, TransactionStatus.VERIFIED_MANUAL]
            ),
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
        )
    )

    # Add category filter if detected (Rule 3.2)
    if detected_category:
        query_builder = query_builder.filter(Transaction.category == detected_category)

    # Step 4: Execute query and calculate result
    transactions = query_builder.all()
    total_amount = sum(t.amount for t in transactions)
    transaction_count = len(transactions)

    # Step 5: Generate natural language response
    if detected_category and detected_period:
        # Rule 3.2: Category + Period
        if detected_period == "today":
            period_text = "hoy"
        elif detected_period == "week":
            period_text = "esta semana"
        elif detected_period == "month":
            period_text = "este mes"
        else:
            period_text = f"en los últimos {days_back} días"

        response_text = f"Has gastado ${total_amount:.2f} en {detected_category.lower()} {period_text}."

    elif detected_category:
        # Rule 3.2: Category only (default to month)
        response_text = (
            f"En total has gastado ${total_amount:.2f} en {detected_category.lower()}."
        )

    elif detected_period:
        # Rule 3.1: Period only
        if detected_period == "today":
            period_text = "hoy"
        elif detected_period == "week":
            period_text = "esta semana"
        elif detected_period == "month":
            period_text = "este mes"
        else:
            period_text = f"en los últimos {days_back} días"

        response_text = f"Has gastado ${total_amount:.2f} en total {period_text}."

    else:
        # Default: total spending (Rule 3.1 default)
        response_text = f"En total has gastado ${total_amount:.2f} este mes."
        detected_period = "month"

    # Add transaction count context
    if transaction_count == 0:
        response_text = (
            response_text.replace(f"${total_amount:.2f}", "$0.00")
            + " No se encontraron transacciones."
        )
    elif transaction_count == 1:
        response_text += f" (1 transacción)"
    else:
        response_text += f" ({transaction_count} transacciones)"

    return {
        "query": query,
        "response": response_text,
        "total_amount": total_amount,
        "period": detected_period,
        "category": detected_category,
        "transaction_count": transaction_count,
    }


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get user by email.
    
    Args:
        db: Database session
        email: User email to retrieve
        
    Returns:
        User: User object if found, None otherwise
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Creates a new user in the database with a hashed password.
    
    Args:
        db: Database session
        user: User creation schema with email, name, and password
        
    Returns:
        User: The newly created user object
    """
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email, name=user.name, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> models.User | bool:
    """Authenticates a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain password to verify
        
    Returns:
        User: User object if authentication successful, False otherwise
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user
