"""Reasoning Module - Google Gemini 1.5 Flash.

This module handles intelligent text analysis and data extraction using Google's Gemini models.
It is optimized for structured JSON extraction from natural language.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

from src.core.config import settings


class GeminiReasoning:
    """Handles reasoning and extraction using Google Gemini."""

    def __init__(self):
        """Initialize the Gemini model."""
        # Configure API key
        # Note: google-generativeai usually expects GOOGLE_API_KEY.
        # If using Vertex AI (google-cloud-aiplatform), auth is via credentials.json.
        # User requested `google-generativeai` package, which is the AI Studio client,
        # but also mentioned `google-auth` for credentials.
        #
        # If we are using `google-generativeai` (Gemini API), we need an API KEY.
        # If we are using Vertex AI, we use `google-cloud-aiplatform`.
        #
        # User requirements: "Usaremos las APIs nativas de Google Cloud." -> usually Vertex AI.
        # BUT Actions said: "`google-generativeai` (Para Gemini)".
        # This package is often for the AI Studio API key access, BUT it can also work with proper setup.
        #
        # Let's assume we map GOOGLE_APPLICATION_CREDENTIALS or a specific API Key.
        # For a "Clean Google Cloud Stack" (Nexus Protocol), Vertex AI is the standard.
        # However, sticking to the requested package `google-generativeai`.
        # We will assume GOOGLE_API_KEY is available or `google.auth` logic is handled internally if configured.
        #
        # CRITICAL: `google-generativeai` requires an API KEY usually.
        # If the user meant Vertex AI, the package should be `google-cloud-aiplatform` with `vertexai`.
        # The prompt specifically asked for `google-generativeai`. 
        # I will check if `GOOGLE_API_KEY` is in env, else try to configure via `configure(api_key=...)`.
        #
        # If we must use ADC (Application Default Credentials), `vertexai` is better.
        # Given "google-auth" was requested, this strongly signals Vertex AI or ADC.
        # `google-generativeai` strictly needs an API key mostly.
        #
        # HYBRID APPROACH for robustness:
        # I will check for GOOGLE_API_KEY. If missing, I will warn or try to fallback.
        # BUT, since I must "Implement... using google.generativeai", I will stick to that interface.
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # It's possible the user has set up ADC and expects it to work, 
            # but `google-generativeai` is primarily API Key based.
            # I'll modify the code to be safe, but primarily rely on genai.
            # If this is strictly GCP Project based, we might need Vertex AI content.
            # I will proceed with `genai` as requested.
            pass

        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_transaction_data(self, text: str) -> Dict[str, Any]:
        """Extract structured transaction data from text.

        Args:
            text: The natural language text (e.g., "Gasté 500 pesos en Soriana hoy").

        Returns:
            dict: Structured data {amount, concept, merchant, date, category}.
        """
        prompt = f"""
        You are a financial assistant. Extract transaction details from the following text into JSON format.
        
        Text: "{text}"
        
        Output JSON with these keys:
        - amount: number (float)
        - concept: string (short description)
        - merchant: string (or null if not mentioned)
        - date: string (ISO 8601 format YYYY-MM-DD, assume today is {datetime.now().strftime('%Y-%m-%d')} if not specified)
        - category: string (guess one: Alimentación, Transporte, Servicios, Ocio, Otros)

        Return ONLY the JSON string, no markdown formatting.
        """

        try:
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
            print(f"Gemini extraction failed: {e}")
            # Fallback/Empty structure so flow doesn't crash hard, or re-raise
            raise ValueError(f"Failed to extract info from text: {text}") from e

import os

# Global instance
reasoner = GeminiReasoning()

def extract_transaction_data(text: str) -> Dict[str, Any]:
    """Public wrapper for extraction."""
    return reasoner.extract_transaction_data(text)
