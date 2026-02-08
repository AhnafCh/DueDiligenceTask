"""Index Manager for orchestrating multi-layer indexing."""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from src.indexing.layers.semantic import SemanticLayer, SearchResult
from src.indexing.layers.citation import CitationLayer
from src.models.project import Project, ProjectStatus, ScopeType
from src.models.document import Document
from src.storage.db.database import get_db

logger = logging.getLogger(__name__)


class IndexManager:
    """
    Orchestrates the multi-layer indexing process.
    Manages semantic and citation layers, and handles project invalidation.
    """
    
    def __init__(self):
        self.semantic_layer = SemanticLayer()
        self.citation_layer = CitationLayer()
        
    def add_document(self, document_id: str, chunks: List[str], chunk_ids: List[str]):
        """
        Add document chunks to all index layers.
        
        Args:
            document_id: ID of the document
            chunks: List of chunk texts
            chunk_ids: List of chunk IDs
        """
        if not chunks:
            return
            
        logger.info(f"Adding document {document_id} to indices ({len(chunks)} chunks)")
        
        # Add to semantic layer
        self.semantic_layer.add_chunks(chunks, chunk_ids)
        
        # Add to citation layer
        # For now, we use the same chunks. In future, we might use smaller chunks.
        self.citation_layer.add_chunks(chunks, chunk_ids)
        
        # Invalidate ALL_DOCS projects
        self._invalidate_all_docs_projects()
        
    def search(self, query: str, k: int = 5) -> List[SearchResult]:
        """
        Search primarily using semantic layer.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of SearchResult objects
        """
        return self.semantic_layer.search(query, k)

    def _invalidate_all_docs_projects(self):
        """
        Mark all projects with scope_type='ALL_DOCS' as OUTDATED.
        This forces them to re-evaluate answers against the new document.
        """
        try:
            # Create a new session for this operation
            db = next(get_db())
            
            projects = db.query(Project).filter(
                Project.scope_type == ScopeType.ALL_DOCS,
                Project.status != ProjectStatus.OUTDATED
            ).all()
            
            count = 0
            for project in projects:
                project.status = ProjectStatus.OUTDATED
                project.updated_at = datetime.utcnow()
                count += 1
                
            db.commit()
            if count > 0:
                logger.info(f"Invalidated {count} ALL_DOCS projects due to new document")
                
        except Exception as e:
            logger.error(f"Failed to invalidate projects: {e}")
            # Don't raise, as indexing itself succeeded
            
    def clear_all(self):
        """Clear all indices."""
        self.semantic_layer.clear()
        self.citation_layer.clear()
        logger.info("Cleared all indices")
