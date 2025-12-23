"""Audio Transcription Module - Google Cloud Speech-to-Text v2 (Chirp).

This module handles audio transcription using the latest Google Cloud Speech-to-Text v2 API.
It specifically targets the 'chirp' model (USM) for high-accuracy Spanish transcription.
"""

import os
from typing import BinaryIO, Union

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import (ExplicitDecodingConfig,
                                          RecognitionConfig,
                                          RecognitionFeatures,
                                          RecognizeRequest)

from src.core.config import settings


class Transcriber:
    """Handles audio transcription using Google Cloud Speech-to-Text v2."""

    def __init__(self):
        """Initialize the SpeechClient with updated endpoint for v2."""
        # Use regional endpoint if location is provided, else global
        # Note: Chirp often requires specific regional endpoints (e.g. us-central1)
        location = settings.GOOGLE_LOCATION
        api_endpoint = f"{location}-speech.googleapis.com"

        client_options = ClientOptions(api_endpoint=api_endpoint)
        self.client = SpeechClient(client_options=client_options)
        self.project_id = settings.GOOGLE_PROJECT_ID
        self.location = location

    async def transcribe(
        self, audio_content: bytes, language_code: str = "es-MX"
    ) -> str:
        """Transcribe audio bytes to text using the Chirp model.

        Args:
            audio_content: Raw audio bytes.
            language_code: Language code (default: es-MX).

        Returns:
            str: The transcribed text.

        Raises:
            Exception: If transcription fails.
        """
        parent = f"projects/{self.project_id}/locations/{self.location}"
        recognizer_id = f"numa-chirp-v3-{language_code.lower().replace('-', '')}"
        recognizer_name = f"{parent}/recognizers/{recognizer_id}"

        # Logic to check/create recognizer involves calling API.
        # For this prototype, we rely on lazy creation in the exception handler.

        config = RecognitionConfig(
            explicit_decoding_config=ExplicitDecodingConfig(
                encoding="WEBM_OPUS",
                sample_rate_hertz=48000,  # Standard for WebM
                audio_channel_count=1,
            ),
            model="latest_long",
            language_codes=[language_code],
            features=RecognitionFeatures(
                enable_word_time_offsets=False,
                enable_automatic_punctuation=True,
            ),
        )

        request = RecognizeRequest(
            recognizer=recognizer_name,
            config=config,
            content=audio_content,
        )

        try:
            response = self.client.recognize(request=request)
        except Exception as e:
            # Check for standard Google API NotFound error
            # It might come as ServiceUnavailable or NotFound depending on exact path state
            error_str = str(e)
            if "404" in error_str or "NotFound" in error_str:
                print(f"Recognizer {recognizer_id} not found. Creating...")
                await self._create_recognizer(parent, recognizer_id, language_code)
                # Retry once
                response = self.client.recognize(request=request)
            else:
                raise e

        # Concatenate results
        transcription = ""
        for result in response.results:
            if result.alternatives:
                transcription += result.alternatives[0].transcript + " "

        return transcription.strip()

    async def _create_recognizer(
        self, parent: str, recognizer_id: str, language_code: str
    ):
        """Creates a Chirp recognizer."""
        from google.cloud.speech_v2.types import (CreateRecognizerRequest,
                                                  Recognizer)

        recognizer = Recognizer(
            default_recognition_config=RecognitionConfig(
                explicit_decoding_config=ExplicitDecodingConfig(
                    encoding="WEBM_OPUS",
                    sample_rate_hertz=48000,
                    audio_channel_count=1,
                ),
                model="latest_long",
                language_codes=[language_code],
                features=RecognitionFeatures(
                    enable_automatic_punctuation=True,
                ),
            )
        )

        request = CreateRecognizerRequest(
            parent=parent,
            recognizer_id=recognizer_id,
            recognizer=recognizer,
        )

        operation = self.client.create_recognizer(request=request)
        print(f"Waiting for recognizer {recognizer_id} creation...")
        operation.result(timeout=120)  # Wait for completion
        print("Recognizer created.")


# Global instance
transcriber = Transcriber()


async def transcribe_audio(audio_bytes: bytes, language: str = "es-MX") -> str:
    """Public wrapper for the transcriber."""
    return await transcriber.transcribe(audio_bytes, language)
