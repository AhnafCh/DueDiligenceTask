"""Semantic indexing layer."""
import logging
from typing import List, Optional
from dataclasses import dataclass

from src.storage.faiss_store import FAISSStore
from src.services.embedding_service import get_embedding_service, EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    chunk_id: str
    score: float
    text: Optional[str] = None
    metadata: Optional[dict] = None


class SemanticLayer:
    """
    Manages the semantic search layer of the index.
    Responsible for embedding and retrieving chunks based on meaning.
    """
    
    def __init__(self):
        self.store = FAISSStore(index_name="semantic_layer")
        self.embedding_service = get_embedding_service()

    def add_chunks(self, texts: List[str], chunk_ids: List[str]):
        """
        Generate embeddings and add chunks to the semantic index.
        
        Args:
            texts: List of chunk texts
            chunk_ids: List of unique chunk identifiers
        """
        if not texts:
            return

        try:
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
            self.store.add_vectors(embeddings, chunk_ids)
            logger.info(f"Added {len(texts)} chunks to semantic layer")
        except Exception as e:
            logger.error(f"Failed to add chunks to semantic layer: {e}")
            raise

    def search(self, query: str, k: int = 5) -> List[SearchResult]:
        """
        Search for semantically similar chunks.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of SearchResult objects
        """
        try:
            query_vector = self.embedding_service.generate_query_embedding(query)
            ids, distances = self.store.search(query_vector, k)
            
            results = []
            for chunk_id, dist in zip(ids, distances):
                # Distance in FAISS L2 is squared Euclidean distance.
                # Smaller is better. Convert to similarity score if needed.
                # For L2, 0 is identical.
                results.append(SearchResult(chunk_id=chunk_id, score=dist))
                
            return results
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def clear(self):
        """Clear the semantic index."""
        self.store.clear()
