"""Finance Core Service - Business Logic (Public Interface).

This module contains the core financial business logic as specified in LOGIC.md.
This is the PUBLIC INTERFACE of the FinanceCore module.

PROTOCOLO NEXUS: Other modules must ONLY import from this file, never from
internal modules like models.py, repository.py, etc.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.modules.finance_core.models import Transaction, TransactionStatus, User
from src.modules.finance_core import schemas
from src.core import auth


# ============================================================================
# USER MANAGEMENT
# ============================================================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email.
    
    Args:
        db: Database session
        email: User email to retrieve
        
    Returns:
        User: User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    """Creates a new user in the database with a hashed password.
    
    Args:
        db: Database session
        user: User creation schema with email, name, and password
        
    Returns:
        User: The newly created user object
    """
    hashed_password = auth.get_password_hash(user.password)
    db_user = User(
        email=user.email, name=user.name, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticates a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain password to verify
        
    Returns:
        User: User object if authentication successful, None otherwise
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not auth.verify_password(password, user.hashed_password):
        return None
    return user


# ============================================================================
# TRANSACTION MANAGEMENT
# ============================================================================

def create_provisional_transaction(
    db: Session, 
    user_id: int, 
    amount: float, 
    concept: str,
    merchant: Optional[str] = None,
    category: Optional[str] = None,
    transaction_date: Optional[datetime] = None
) -> Transaction:
    """Create a provisional transaction.
    
    Implements LOGIC.md Rule 2.1 (Creación Provisional por Voz) - Step 3.
    Enhanced to store AI-extracted metadata if available.
    
    Args:
        db: Database session
        user_id: ID of the user creating the transaction
        amount: Transaction amount
        concept: Transaction concept/description
        merchant: Optional merchant name
        category: Optional category
        transaction_date: Optional transaction date
        
    Returns:
        Transaction: The newly created provisional transaction
    """
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        concept=concept,
        status=TransactionStatus.PROVISIONAL,
        merchant=merchant,
        category=category,
        transaction_date=transaction_date
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction


def verify_transaction_with_document(
    db: Session, 
    transaction_id: int, 
    amount: float,
    merchant: str,
    transaction_date: datetime,
    category: Optional[str] = None
) -> Transaction:
    """Verify a provisional transaction using document data.
    
    Implements LOGIC.md Rule 2.2 (Verificación por Comprobante).
    
    Args:
        db: Database session
        transaction_id: ID of the transaction to verify
        amount: Exact amount from document
        merchant: Merchant name from document
        transaction_date: Transaction date from document
        category: Optional pre-assigned category
        
    Returns:
        Transaction: The updated verified transaction
        
    Raises:
        HTTPException: If transaction not found or not in provisional state
    """
    # Find the transaction
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Verify transaction is in provisional state
    if transaction.status != TransactionStatus.PROVISIONAL:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is not in provisional state. Current state: {transaction.status.value}",
        )
    
    # Update transaction with document data
    transaction.amount = amount  # Document amount is source of truth
    transaction.merchant = merchant
    transaction.transaction_date = transaction_date
    transaction.transaction_time = transaction_date.strftime("%H:%M:%S")
    
    # Change status to verified
    transaction.status = TransactionStatus.VERIFIED
    
    # Assign category if provided
    if category:
        transaction.category = category
    
    # Save changes
    db.commit()
    db.refresh(transaction)
    
    return transaction


def verify_transaction_manually(db: Session, transaction_id: int, category: Optional[str] = None) -> Transaction:
    """Verify a provisional transaction manually without a source document.
    
    Implements LOGIC.md Rule 2.3 (Creación Verificada Manualmente).
    
    Args:
        db: Database session
        transaction_id: ID of the transaction to verify manually
        category: Optional pre-assigned category
        
    Returns:
        Transaction: The updated verified transaction
        
    Raises:
        HTTPException: If transaction not found or not in provisional state
    """
    # Find the transaction
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Verify transaction is in provisional state
    if transaction.status != TransactionStatus.PROVISIONAL:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is not in provisional state. Current state: {transaction.status.value}",
        )
    
    # Change status to verified_manual
    transaction.status = TransactionStatus.VERIFIED_MANUAL
    
    # Assign category if provided
    if category:
        transaction.category = category
    
    # Save changes
    db.commit()
    db.refresh(transaction)
    
    return transaction


def get_user_transactions(
    db: Session, 
    user_id: int, 
    status: Optional[TransactionStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None
) -> List[Transaction]:
    """Get transactions for a user with optional filters.
    
    INVARIANT: All queries MUST be filtered by user_id (multi-tenancy).
    
    Args:
        db: Database session
        user_id: ID of the user
        status: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        category: Optional category filter
        
    Returns:
        List[Transaction]: List of transactions matching filters
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if status:
        query = query.filter(Transaction.status == status)
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    return query.all()


def calculate_user_spending(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None
) -> float:
    """Calculate total spending for a user.
    
    Implements LOGIC.md Rule 3.1 (Consulta de Gasto Total) and 3.2 (Por Categoría).
    
    INVARIANT: All queries MUST be filtered by user_id (multi-tenancy).
    
    Args:
        db: Database session
        user_id: ID of the user
        start_date: Optional start date filter
        end_date: Optional end date filter
        category: Optional category filter
        
    Returns:
        float: Total spending amount
    """
    query = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.status.in_([TransactionStatus.VERIFIED, TransactionStatus.VERIFIED_MANUAL])
        )
    )
    
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    total = query.scalar()
    return total if total else 0.0


def get_spending_breakdown(db: Session, user_id: int, group_by: str = "category") -> dict:
    """Get spending breakdown grouped by category or merchant.
    
    Args:
        db: Database session
        user_id: ID of the user
        group_by: Field to group by ("category" or "merchant")
        
    Returns:
        dict: Dictionary with breakdown data
    """
    if group_by == "category":
        results = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.status.in_([TransactionStatus.VERIFIED, TransactionStatus.VERIFIED_MANUAL]),
                Transaction.category.isnot(None)
            )
        ).group_by(Transaction.category).all()
        
        return {
            "breakdown": [
                {"category": r.category, "total": r.total, "count": r.count}
                for r in results
            ]
        }
    
    elif group_by == "merchant":
        results = db.query(
            Transaction.merchant,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.status.in_([TransactionStatus.VERIFIED, TransactionStatus.VERIFIED_MANUAL]),
                Transaction.merchant.isnot(None)
            )
        ).group_by(Transaction.merchant).all()
        
        return {
            "breakdown": [
                {"merchant": r.merchant, "total": r.total, "count": r.count}
                for r in results
            ]
        }
    
    else:
        raise ValueError(f"Invalid group_by value: {group_by}")
