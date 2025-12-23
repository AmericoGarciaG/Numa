"""SQLAlchemy models for Numa.

This module defines the core entities as specified in LOGIC.md:
- User: Represents the owner of financial data
- Transaction: Represents a single financial movement (expense or income)
- SourceDocument: Represents the original receipt of a transaction
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship

from src.core.database import Base


class TransactionStatus(enum.Enum):
    """Transaction status enum as defined in LOGIC.md Rule 2.1, 2.2, 2.3."""

    PROVISIONAL = "provisional"
    VERIFIED = "verified"
    VERIFIED_MANUAL = "verified_manual"


class TransactionType(enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    DEBT = "debt"


class User(Base):
    """User entity - represents the owner of financial data.

    As specified in LOGIC.md: "User: Representa al propietario de los datos
    financieros. Todo está asociado a un User."
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="user")


class Transaction(Base):
    """Transaction entity - represents a single financial movement.

    As specified in LOGIC.md: "Transaction: Representa un único movimiento
    financiero (gasto o ingreso)."

    Status follows the rules defined in LOGIC.md:
    - provisional: Created via voice command (Rule 2.1)
    - verified: Verified via source document (Rule 2.2)
    - verified_manual: Manually verified without document (Rule 2.3)
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Core transaction data
    type = Column(
        Enum(TransactionType), nullable=False, default=TransactionType.EXPENSE
    )
    amount = Column(Float, nullable=False)
    concept = Column(String, nullable=False)  # Description from voice command

    # Status as defined in LOGIC.md
    status = Column(Enum(TransactionStatus), nullable=False)

    # Additional data populated during verification (Rule 2.2)
    merchant = Column(String, nullable=True)  # "Comercio" from document
    transaction_date = Column(DateTime, nullable=True)  # "Fecha" from document
    transaction_time = Column(String, nullable=True)  # "Hora" from document

    # Categorization (Rule 2.4)
    category = Column(String, nullable=True)

    # System metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    source_documents = relationship("SourceDocument", back_populates="transaction")


class SourceDocument(Base):
    """SourceDocument entity - represents the original receipt of a transaction.

    As specified in LOGIC.md: "SourceDocument: Representa el comprobante
    original de una transacción (imagen, PDF, etc.)."
    """

    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)

    # Document metadata
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "image/jpeg", "application/pdf", etc.
    file_size = Column(Integer, nullable=False)

    # Extracted data (populated by LLM multimodal analysis - Rule 2.2)
    extracted_data = Column(Text, nullable=True)  # JSON string with extracted info

    # System metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction = relationship("Transaction", back_populates="source_documents")
