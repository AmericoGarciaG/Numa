"""Reasoning Module - Google Vertex AI (Gemini).

This module handles intelligent text analysis and data extraction using Google's Vertex AI (Gemini).
It is optimized for structured JSON extraction from natural language.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

from src.core.config import settings


class IncompleteInfoError(ValueError):
    pass


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
        - merchant: string or null (the source for INCOME, the creditor for DEBT, or the store for EXPENSE. If the store or vendor is not explicitly mentioned, you MUST return null for merchant. Do NOT copy the concept into the merchant field.)
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

        Validation rules:
        - If the text does not contain enough information to form a valid transaction (for example, it is missing both amount and concept), return an empty JSON array [] instead of inventing values.
        - If a concept is mentioned but no amount is specified, you MUST return an empty JSON array [] and treat this as an invalid transaction. Do NOT return a transaction with amount 0.

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
                data_list: List[Dict[str, Any]] = [data]
            else:
                data_list = list(data)
            valid_items: List[Dict[str, Any]] = []
            last_reason = ""
            for item in data_list:
                is_valid, reason = self._is_valid_transaction(item)
                if is_valid:
                    valid_items.append(item)
                else:
                    last_reason = reason or last_reason
            if not valid_items:
                raise IncompleteInfoError(
                    last_reason or "Incomplete transaction information."
                )
            return valid_items
        except Exception as e:
            print(f"Vertex AI Gemini extraction failed: {e}")
            # Re-raise to be handled by caller
            raise ValueError(f"Failed to extract info from text: {text}") from e

    def _is_valid_transaction(
        self, transaction_data: Dict[str, Any]
    ) -> Tuple[bool, str]:
        concept_raw = transaction_data.get("concept")
        concept_text = (concept_raw or "").strip().lower()
        amount_raw = transaction_data.get("amount", 0)
        try:
            amount_value = float(amount_raw)
        except (TypeError, ValueError):
            amount_value = 0.0
        blacklist = ["gasto", "ingreso", "deuda", "compra", "pago", "dinero"]
        if amount_value <= 0:
            if concept_text in blacklist or len(concept_text) < 3:
                return False, "Concepto demasiado genérico y sin monto."
            return False, "Monto obligatorio para registrar la transacción."
        return True, ""

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

    def analyze_input_stream(self, text: str) -> Dict[str, Any]:
        normalized = (text or "").strip()
        if not normalized or len(normalized) < 2:
            return {"intent": "NOISE"}

        macro_prompt = f"""
        You are an intent classifier for a Spanish-speaking assistant.

        User utterance: "{text}"

        Classify the utterance into one of these domains:
        - "META": Questions or commands about the assistant or system itself
          (for example: who are you, change language, delete my data).
        - "SOCIAL": Greetings, small talk, jokes or casual conversation not directly
          about money.
        - "FINANCIAL": Any request, statement or command related to money, expenses,
          income, debts, prices, budgets or financial reports.

        Output a single JSON object with this structure:
        {{
          "domain": "META" | "SOCIAL" | "FINANCIAL"
        }}

        Output only the JSON object.
        """

        try:
            response = self.model.generate_content(macro_prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            macro_data = json.loads(clean_text)
            domain = (macro_data.get("domain") or "").strip().upper()
        except Exception as e:
            print(f"Vertex AI Gemini macro intent classification failed: {e}")
            domain = "FINANCIAL"

        if domain != "FINANCIAL":
            return {"intent": domain}

        detail_prompt = f"""
        You are a financial intent classifier for a Spanish-speaking assistant.

        Financial utterance: "{text}"

        Classify it into one of these options:
        - "READ": The user is asking for information about past or current financial
          data (for example: questions about how much they spent, balances, summaries).
        - "AMBIGUOUS": The user expresses an intention to register a movement but the
          statement is incomplete, typically when it only contains generic type words
          like "gasto", "ingreso" or "deuda" without a specific object or concept.
        - "WRITE": The user describes a financial movement with at least one concrete
          concept or object (for example: tacos, luz, renta, camisa, uber, netflix),
          even if the amount is not mentioned.

        Special rules:
        - If the utterance is only one generic word like "gasto", "ingreso" or "deuda",
          or a close variant with punctuation, classify it as "AMBIGUOUS".
        - Do not classify as "READ" if there is no clear question form.
        - When in doubt between "AMBIGUOUS" and "WRITE", prefer "AMBIGUOUS".

        Output a single JSON object with this structure:
        {{
          "resolution": "READ" | "AMBIGUOUS" | "WRITE"
        }}

        Output only the JSON object.
        """

        try:
            response = self.model.generate_content(detail_prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            detail_data = json.loads(clean_text)
            resolution = (detail_data.get("resolution") or "").strip().upper()
            if resolution not in ("READ", "AMBIGUOUS", "WRITE"):
                resolution = "WRITE"
        except Exception as e:
            print(f"Vertex AI Gemini financial resolution classification failed: {e}")
            resolution = "WRITE"

        return {"intent": resolution, "domain": "FINANCIAL"}

    def classify_intent(self, text: str) -> Dict[str, Any]:
        prompt = f"""
        You are a financial assistant. Analyze the user's utterance and classify the primary intent.

        User utterance: "{text}"

        You must output a single JSON object with this structure:
        {{
          "intent": "WRITE_LOG" | "QUERY" | "CHAT" | "UNKNOWN",
          "confidence": float
        }}

        Definitions:
        - WRITE_LOG: The user wants to register expenses, income, debts, or financial plans AND clearly provides both a concrete concept and an explicit amount.
          Examples: "Gasté 50 en comida", "Registra un pago de 200 de luz", "Me pagaron la nómina de 15000".
        - QUERY: The user is asking for financial information about past or current data.
          Examples: "¿Cuánto gasté?", "¿Tengo saldo?", "¿Cuánto he gastado hoy en comida?".
        - CHAT: Greetings, non-financial questions, or general small talk.
          Examples: "Hola", "¿Quién eres?", "Cuéntame un chiste".
        - UNKNOWN: Use this when the utterance is unintelligible, too short to understand (for example fewer than three meaningful words), or clearly lacks any financial context and cannot be confidently mapped to another intent.

        Rules:
        - Choose the intent that best matches the entire utterance.
        - If the user mentions only a concept without an explicit amount (for example: "gasto de comida", "compras del súper" without numbers), do NOT classify it as "WRITE_LOG". Prefer "CHAT" or "UNKNOWN" and let the system ask for clarification.
        - If you are not at least 0.7 confident about a specific intent, prefer returning "CHAT" or "UNKNOWN" and set confidence below 0.7.
        - If the utterance is a single generic word such as "gasto", "ingreso" or "deuda", treat it as incomplete and classify it as "UNKNOWN" or "CHAT", not "WRITE_LOG".
        - confidence must be a float between 0 and 1.

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
            intent = data.get("intent")
            confidence = data.get("confidence")
            try:
                confidence_value = float(confidence)
            except (TypeError, ValueError):
                confidence_value = None
            if confidence_value is not None and confidence_value < 0.7:
                if intent in ("WRITE_LOG", "QUERY"):
                    data["intent"] = "UNKNOWN"
            text_normalized = (text or "").strip().lower()
            if text_normalized in ("gasto", "ingreso", "deuda"):
                data["intent"] = "UNKNOWN"
            return data
        except Exception as e:
            print(f"Vertex AI Gemini intent classification failed: {e}")
            raise ValueError(f"Failed to classify intent: {text}") from e

    def generate_chat_response(self, text: str, mode: str = "CHAT") -> str:
        prompt = f"""
        You are Numa, a Spanish-speaking financial assistant.
        You can register expenses, income and debts, and answer questions about the user's balance and spending.

        Interaction mode: {mode}
        User utterance: "{text}"

        Instructions:
        - If the user asks about personal finances (spending, income, debts, budgets, goals, savings), answer briefly and concretely in Spanish.
        - If the user asks about topics unrelated to finances, respond in Spanish explaining that you are a financial assistant and invite them to ask about their money, spending, income or debts.
        - Keep the answer under three short sentences.
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

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


def analyze_query_intent(text: str, current_date: str) -> Dict[str, Any]:
    return reasoner.analyze_query_intent(text, current_date)


def analyze_confirmation_intent(text: str) -> Dict[str, Any]:
    return reasoner.analyze_confirmation_intent(text)


def classify_intent(text: str) -> Dict[str, Any]:
    return reasoner.classify_intent(text)


def generate_chat_response(text: str, mode: str = "CHAT") -> str:
    return reasoner.generate_chat_response(text, mode)


def analyze_input_stream(text: str) -> Dict[str, Any]:
    return reasoner.analyze_input_stream(text)
