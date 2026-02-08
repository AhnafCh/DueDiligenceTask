import logging
from typing import List, Dict, Any, Optional, Type, TypeVar
import google.generativeai as genai
from pydantic import BaseModel
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMService:
    """
    Service for interacting with Google Gemini models.
    """
    
    def __init__(self):
        settings = get_settings()
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not set in configuration")
            
        genai.configure(api_key=settings.google_api_key)
        # Using gemini-2.5-flash for speed and efficiency in RAG agent
        self.model_name = "gemini-2.5-flash" 
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized LLMService with model: {self.model_name}")

    def generate_text(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Generate plain text response.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"LLM text generation failed: {e}")
            raise

    def generate_structured(self, prompt: str, response_model: Type[T], temperature: float = 0.0) -> T:
        """
        Generate structured data using Pydantic models.
        """
        try:
            # Gemini support for constrained output (JSON mode)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                    # Some versions/models support response_schema directly
                )
            )
            # Basic JSON parsing if it returns text
            import json
            data = json.loads(response.text)
            return response_model.model_validate(data)
        except Exception as e:
            logger.error(f"LLM structured generation failed: {e}")
            # Fallback or re-raise
            raise
