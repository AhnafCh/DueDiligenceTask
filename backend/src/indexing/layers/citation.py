"""Citation indexing layer."""
import logging
from typing import List

from src.storage.faiss_store import FAISSStore
from src.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class CitationLayer:
    """
    Manages the citation layer of the index.
    Designed for precise retrieval of specific facts or quotes, 
    potentially using smaller chunks or different embedding strategies.
    
    For now, it mirrors the semantic layer but is kept separate to allow 
    for different chunking/indexing strategies in the future (e.g. dense retrieval vs sparse).
    """
    
    def __init__(self):
        self.store = FAISSStore(index_name="citation_layer")
        self.embedding_service = get_embedding_service()

    def add_chunks(self, texts: List[str], chunk_ids: List[str]):
        """
        Add chunks to the citation index.
        """
        if not texts:
            return

        try:
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
            self.store.add_vectors(embeddings, chunk_ids)
            logger.info(f"Added {len(texts)} chunks to citation layer")
        except Exception as e:
            logger.error(f"Failed to add chunks to citation layer: {e}")
            raise

    def search(self, query: str, k: int = 5):
        """
        Search for citation chunks.
        """
        try:
            query_vector = self.embedding_service.generate_query_embedding(query)
            return self.store.search(query_vector, k)
        except Exception as e:
            logger.error(f"Citation search failed: {e}")
            return [], []
            
    def clear(self):
        """Clear the citation index."""
        self.store.clear()
