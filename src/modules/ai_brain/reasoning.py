"""Reasoning Module - Google Vertex AI (Gemini).

This module handles intelligent text analysis and data extraction using Google's Vertex AI (Gemini).
It is optimized for structured JSON extraction from natural language.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

from src.core.config import settings


class GeminiReasoning:
    """Handles reasoning and extraction using Google Vertex AI (Gemini)."""

    def __init__(self):
        """Initialize the Vertex AI Gemini model."""
        # Initialize Vertex AI with project and location from settings
        # This will automatically use GOOGLE_APPLICATION_CREDENTIALS
        vertexai.init(
            project=settings.GOOGLE_PROJECT_ID, location=settings.GOOGLE_LOCATION
        )

        # gemini-2.0-flash-exp detected as available by diagnostic
        self.model = GenerativeModel("gemini-2.0-flash-exp")

    def extract_transaction_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract one or more structured transactions from text.

        Args:
            text: The natural language text (e.g., "Gasté 500 pesos en Soriana hoy").

        Returns:
            list[dict]: List of structured transactions.
        """
        prompt = f"""
        You are a financial assistant. Analyze the text and identify all distinct financial actions.
        You MUST return a JSON ARRAY (top-level) of transaction objects, even if there is only one.

        Text: "{text}"

        For EACH financial action, output an object with these keys:
        - type: string (must be one of: 'EXPENSE', 'INCOME', 'DEBT')
        - amount: number (float)
        - concept: string (short description)
        - merchant: string (the source for INCOME, the creditor for DEBT, or the store for EXPENSE. If the store or vendor is mentioned, you must fill this field with a non-empty string.)
        - date: string (ISO 8601 format YYYY-MM-DD, assume today is {datetime.now().strftime('%Y-%m-%d')} if not specified)
        - category: string. You MUST choose exactly one from this closed taxonomy:
          - Esenciales: "Vivienda", "Servicios", "Despensa", "Transporte", "Salud", "Educación"
          - Discrecionales: "Restaurantes", "Café/Snacks", "Ocio", "Ropa/Calzado", "Hogar/Muebles", "Electrónica", "Cuidado Personal", "Regalos", "Compras"
          - Movimientos financieros: "Deuda", "Inversión", "Ingreso", "Transferencia"

        Extra rule for "gastos hormiga":
        - If the expense is small (less than 200 MXN) and happens in convenience stores, coffee shops,
          kiosks, or similar places, you should prioritize classifying it as "Café/Snacks" or "Compras".

        Avoid using generic categories:
        - Avoid the category "Otros" or any variation.
        - Avoid using "Compras" unless it is absolutely impossible to map the item into "Ropa/Calzado", "Hogar/Muebles", "Electrónica" or "Cuidado Personal".

        Return ONLY the JSON array.
        """

        try:
            # Generate content
            # Set response_mime_type to application/json for guaranteed JSON (if supported by model version)
            # or just rely on prompt instruction for now.
            response = self.model.generate_content(prompt)

            # Clean response if it contains markdown code blocks
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            data = json.loads(clean_text)
            if isinstance(data, dict):
                return [data]
            return data
        except Exception as e:
            print(f"Vertex AI Gemini extraction failed: {e}")
            # Re-raise to be handled by caller
            raise ValueError(f"Failed to extract info from text: {text}") from e

    async def analyze_audio_direct(self, audio_bytes: bytes) -> List[Dict[str, Any]]:
        """Analyze audio bytes directly using Gemini Multimodal capabilities."""
        from vertexai.generative_models import Part

        # Create audio part
        audio_part = Part.from_data(data=audio_bytes, mime_type="audio/webm")

        prompt = f"""
        You are a financial assistant. Listen to the audio and identify all distinct financial actions.
        You MUST return a JSON ARRAY (top-level) of transaction objects, even if there is only one.

        For EACH financial action, output an object with these keys:
        - type: string (must be one of: 'EXPENSE', 'INCOME', 'DEBT')
        - amount: number (float)
        - concept: string (short description)
        - merchant: string (the source for INCOME, the creditor for DEBT, or the store for EXPENSE. If the store or vendor is mentioned, you must fill this field with a non-empty string.)
        - date: string (ISO 8601 format YYYY-MM-DD, assume today is {datetime.now().strftime('%Y-%m-%d')} if not specified)
        - category: string. You MUST choose exactly one from this closed taxonomy:
          - Esenciales: "Vivienda", "Servicios", "Despensa", "Transporte", "Salud", "Educación"
          - Discrecionales: "Restaurantes", "Café/Snacks", "Ocio", "Ropa/Calzado", "Hogar/Muebles", "Electrónica", "Cuidado Personal", "Regalos", "Compras"
          - Movimientos financieros: "Deuda", "Inversión", "Ingreso", "Transferencia"

        Extra rule for "gastos hormiga":
        - If the expense is small (less than 200 MXN) and happens in convenience stores, coffee shops,
          kiosks, or similar places, you should prioritize classifying it as "Café/Snacks" or "Compras".

        Avoid using generic categories:
        - Avoid the category "Otros" or any variation.
        - Avoid using "Compras" unless it is absolutely impossible to map the item into "Ropa/Calzado", "Hogar/Muebles", "Electrónica" or "Cuidado Personal".

        Return ONLY the JSON array.
        """

        try:
            # Gemini 2.0 Flash is multimodal
            response = await self.model.generate_content_async([audio_part, prompt])

            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            data = json.loads(clean_text)
            if isinstance(data, dict):
                return [data]
            return data
        except Exception as e:
            print(f"Vertex AI Gemini Audio analysis failed: {e}")
            raise ValueError("Gemini couldn't understand the audio.") from e

    def analyze_query_intent(self, text: str, current_date: str) -> Dict[str, Any]:
        prompt = f"""
        You are a SQL data analyst. Your job is to translate natural language questions
        about personal finances into structured query filters.

        Current date (ISO): {current_date}
        User question: "{text}"

        You must output a single JSON object with this structure:
        {{
          "intent": "QUERY" | "CHAT",
          "filters": {{
            "start_date": string | null,
            "end_date": string | null,
            "category": string | null,
            "merchant": string | null,
            "type": "EXPENSE" | "INCOME" | "DEBT" | null
          }}
        }}

        Rules:
        - Use "intent": "QUERY" when the user asks for data based on past transactions
          (totals, how much, cuánto gasté, etc.).
        - Use "intent": "CHAT" for greetings, explanations, or questions that do not
          require reading past transactions.
        - start_date and end_date must be ISO dates (YYYY-MM-DD) or null.
        - If the user says "hoy" or "today", use start_date = end_date = current_date.
        - If the user says "ayer" or "yesterday", use the day before current_date for both.
        - If the user says "esta semana" or "this week", use Monday of the current week
          as start_date and current_date as end_date.
        - If the user says "semana pasada" or "last week", use Monday to Sunday of the
          previous week.
        - If the user says "este mes" or "this month", use the first day of the current
          month as start_date and current_date as end_date.
        - category should be one of the taxonomy labels if mentioned (for example:
          Vivienda, Servicios, Despensa, Transporte, Salud, Educación, Restaurantes,
          Café/Snacks, Ocio, Ropa/Calzado, Hogar/Muebles, Electrónica, Cuidado Personal,
          Regalos, Compras, Deuda, Inversión, Ingreso, Transferencia),
          else null.
        - merchant should be a specific vendor or person name if mentioned, else null.
        - type should be "EXPENSE", "INCOME" or "DEBT" if the question clearly refers
          to gastos, ingresos or deudas. Otherwise null.

        Output only the JSON object.
        """

        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            data = json.loads(clean_text)
            return data
        except Exception as e:
            print(f"Vertex AI Gemini query intent analysis failed: {e}")
            raise ValueError(f"Failed to analyze query intent: {text}") from e

    def analyze_confirmation_intent(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        You are a financial assistant specialized in confirmation flows.
        Your job is to detect when the user is confirming or correcting previously
        recorded transactions using natural language.

        User utterance: "{text}"

        You must output a single JSON object with this structure:
        {{
          "intent": "CONFIRM_UPDATE" | "OTHER"
        }}

        Rules:
        - Use "CONFIRM_UPDATE" when the user clearly confirms or updates transactions,
          for example with phrases like "confirmo", "confirmo todo", "sí, está bien",
          "cambia la categoría a Salud", "el gasto fue en Walmart".
        - Use "OTHER" for greetings, small talk, or questions that do not mean
          confirmation or correction of transactions.

        Output only the JSON object.
        """

        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            data = json.loads(clean_text)
            return data
        except Exception as e:
            print(f"Vertex AI Gemini confirmation intent analysis failed: {e}")
            raise ValueError(f"Failed to analyze confirmation intent: {text}") from e


# Global instance
reasoner = GeminiReasoning()


def extract_transaction_data(text: str) -> List[Dict[str, Any]]:
    """Public wrapper for extraction."""
    return reasoner.extract_transaction_data(text)


async def analyze_audio_direct(audio_bytes: bytes) -> List[Dict[str, Any]]:
    """Public wrapper for direct audio analysis."""
    return await reasoner.analyze_audio_direct(audio_bytes)


def analyze_query_intent(text: str, current_date: str) -> Dict[str, Any]:
    return reasoner.analyze_query_intent(text, current_date)


def analyze_confirmation_intent(text: str) -> Dict[str, Any]:
    return reasoner.analyze_confirmation_intent(text)
