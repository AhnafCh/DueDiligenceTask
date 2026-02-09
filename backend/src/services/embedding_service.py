"""Embedding service using Google Generative AI."""
import logging
from typing import List, Optional
from functools import lru_cache
import google.generativeai as genai
from google.generativeai import embed_content

from src.utils.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Google Generative AI."""
    
    def __init__(self):
        """Initialize the embedding service."""
        settings = get_settings()
        
        # Configure Google AI
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=settings.google_api_key)
        self.settings = settings
        self.model_name = settings.embedding_model
        logger.info(f"Initialized EmbeddingService with model: {self.model_name}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using SEMANTIC_SIMILARITY.
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")
        
        try:
            # Using the exact model and task type from the provided documentation/suggestion
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="SEMANTIC_SIMILARITY"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        """
        if not texts:
            raise ValueError("Cannot generate embeddings for empty list")
        
        embeddings: List[List[float]] = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                # Filter/Sanitize batch
                valid_texts = [t if (t and t.strip()) else " " for t in batch]
                
                result = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=valid_texts,
                    task_type="SEMANTIC_SIMILARITY"
                )
                embeddings.extend(result['embedding'])
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}. Falling back to single.")
                for text in batch:
                    if text and text.strip():
                        embeddings.append(self.generate_embedding(text))
                    else:
                        embeddings.append([0.0] * self.settings.embedding_dimension)
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query using SEMANTIC_SIMILARITY.
        """
        if not query or not query.strip():
            raise ValueError("Cannot generate embedding for empty query")
        
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=query,
                task_type="SEMANTIC_SIMILARITY"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise RuntimeError(f"Query embedding generation failed: {e}")


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
