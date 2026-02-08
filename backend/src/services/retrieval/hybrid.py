import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from .semantic import SemanticRetrievalService
from . import RetrievedChunk

logger = logging.getLogger(__name__)

class HybridRetrievalService:
    """
    Orchestrates multiple retrieval strategies.
    Currently focuses on semantic search, but set up for expansion (BM25, Reranking, etc.)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.semantic_service = SemanticRetrievalService(db)

    def search(self, query: str, k: int = 5, document_ids: Optional[List[str]] = None) -> List[RetrievedChunk]:
        """
        Main entry point for retrieval in the RAG agent.
        
        TODO: Add support for filtering by document_ids if project scope is SPECIFIC.
        TODO: Implement query expansion or hybrid lexical search if needed.
        """
        # Placeholder for hybrid logic. For Phase 4 start, we use semantic.
        results = self.semantic_service.retrieve(query, k=k)
        
        # Filter by document_ids if provided
        if document_ids:
            results = [res for res in results if res.document_id in document_ids]
            
        return results
