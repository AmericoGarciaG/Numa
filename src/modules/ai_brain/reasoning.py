"""Reasoning Module - Google Vertex AI (Gemini).

This module handles intelligent text analysis and data extraction using Google's Vertex AI (Gemini).
It is optimized for structured JSON extraction from natural language.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from src.core.config import settings


class GeminiReasoning:
    """Handles reasoning and extraction using Google Vertex AI (Gemini)."""

    def __init__(self):
        """Initialize the Vertex AI Gemini model."""
        # Initialize Vertex AI with project and location from settings
        # This will automatically use GOOGLE_APPLICATION_CREDENTIALS
        vertexai.init(
            project=settings.GOOGLE_PROJECT_ID,
            location=settings.GOOGLE_LOCATION
        )
        
        # gemini-2.0-flash-exp detected as available by diagnostic
        self.model = GenerativeModel("gemini-2.0-flash-exp")

    def extract_transaction_data(self, text: str) -> Dict[str, Any]:
        """Extract structured transaction data from text.

        Args:
            text: The natural language text (e.g., "Gasté 500 pesos en Soriana hoy").

        Returns:
            dict: Structured data {amount, concept, merchant, date, category}.
        """
        # Prompt optimized for JSON extraction
        prompt = f"""
        You are a financial assistant. Extract transaction details from the following text into JSON format.
        
        Text: "{text}"
        
        Output JSON with these keys:
        - amount: number (float)
        - concept: string (short description)
        - merchant: string (or null if not mentioned)
        - date: string (ISO 8601 format YYYY-MM-DD, assume today is {datetime.now().strftime('%Y-%m-%d')} if not specified)
        - category: string (guess one: Alimentación, Transporte, Servicios, Ocio, Otros)

        Return ONLY the JSON string.
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
            
            return json.loads(clean_text)
        except Exception as e:
            print(f"Vertex AI Gemini extraction failed: {e}")
            # Re-raise to be handled by caller
            raise ValueError(f"Failed to extract info from text: {text}") from e


# Global instance
reasoner = GeminiReasoning()

def extract_transaction_data(text: str) -> Dict[str, Any]:
    """Public wrapper for extraction."""
    return reasoner.extract_transaction_data(text)
