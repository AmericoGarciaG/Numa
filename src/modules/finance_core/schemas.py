"""Pydantic schemas for Numa API.

This module defines the API contracts for all entities as specified in AGENTS.md.
Includes base schemas, creation schemas, and complete read schemas for clear API contracts.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from src.modules.finance_core.models import TransactionStatus


# User schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str


class User(UserBase):
    """Complete user schema for API responses."""

    id: int
    created_at: datetime
    transactions: List["Transaction"] = []

    class Config:
        from_attributes = True


# SourceDocument schemas
class SourceDocumentBase(BaseModel):
    """Base source document schema with common fields."""

    filename: str
    file_type: str
    file_size: int


class SourceDocumentCreate(SourceDocumentBase):
    """Schema for source document creation."""

    transaction_id: int
    file_path: str


class SourceDocument(SourceDocumentBase):
    """Complete source document schema for API responses."""

    id: int
    transaction_id: int
    file_path: str
    extracted_data: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    """Base transaction schema with common fields."""

    amount: float
    concept: str


class TransactionCreate(TransactionBase):
    """Schema for transaction creation."""

    user_id: int
    status: TransactionStatus = TransactionStatus.PROVISIONAL


class TransactionUpdate(BaseModel):
    """Schema for transaction updates during verification process."""

    amount: Optional[float] = None
    concept: Optional[str] = None
    status: Optional[TransactionStatus] = None
    merchant: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_time: Optional[str] = None
    category: Optional[str] = None


class Transaction(TransactionBase):
    """Complete transaction schema for API responses."""

    id: int
    user_id: int
    status: TransactionStatus
    merchant: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_time: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source_documents: List[SourceDocument] = []

    class Config:
        from_attributes = True


# Voice command schemas
class VoiceCommandCreate(BaseModel):
    """Schema for voice command input that creates provisional transactions."""

    user_id: int
    audio_text: str  # Transcribed voice command


class VoiceCommandResponse(BaseModel):
    """Schema for voice command response."""

    message: str
    transaction: Transaction


# Query schemas for conversational assistant
class ExpenseQuery(BaseModel):
    """Schema for expense queries in natural language."""

    user_id: int
    query: str  # Natural language query like "How much did I spend this week?"


class ExpenseQueryResponse(BaseModel):
    """Schema for expense query responses."""

    query: str
    response: str
    total_amount: Optional[float] = None
    period: Optional[str] = None
    category: Optional[str] = None


# Chat schemas for conversational assistant (Rules 3.1 and 3.2)
class ChatQuery(BaseModel):
    """Schema for chat queries in natural language."""

    message: str  # Natural language query like "How much did I spend this week?"


class ChatResponse(BaseModel):
    """Schema for chat responses."""

    response: str
    total_amount: Optional[float] = None
    period: Optional[str] = None
    category: Optional[str] = None
    transaction_count: Optional[int] = None


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Update forward references
User.model_rebuild()
