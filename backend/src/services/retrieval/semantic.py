import logging
from typing import List
from sqlalchemy.orm import Session
from src.indexing.manager import IndexManager
from src.storage.db.models import ChunkModel, DocumentModel
from . import RetrievedChunk

logger = logging.getLogger(__name__)

class SemanticRetrievalService:
    """
    Search and retrieve hydrated chunks from the semantic index.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.index_manager = IndexManager()

    def retrieve(self, query: str, k: int = 5) -> List[RetrievedChunk]:
        """
        Perform semantic search and hydrate results from database.
        """
        logger.info(f"Performing semantic retrieval for: {query}")
        
        # 1. Search FAISS index
        search_results = self.index_manager.search(query, k=k)
        
        if not search_results:
            return []
            
        # 2. Extract IDs
        chunk_ids = [res.chunk_id for res in search_results]
        score_map = {res.chunk_id: res.score for res in search_results}
        
        # 3. Hydrate from DB
        db_chunks = (
            self.db.query(ChunkModel, DocumentModel.filename)
            .join(DocumentModel, ChunkModel.document_id == DocumentModel.id)
            .filter(ChunkModel.id.in_(chunk_ids))
            .all()
        )
        
        # 4. Map back to RetrievedChunk and maintain order/scores
        retrieved_chunks = []
        # Create a lookup for DB results
        db_map = {chunk.id: (chunk, filename) for chunk, filename in db_chunks}
        
        for cid in chunk_ids:
            if cid in db_map:
                chunk, filename = db_map[cid]
                retrieved_chunks.append(
                    RetrievedChunk(
                        id=chunk.id,
                        text=chunk.text,
                        score=score_map[cid],
                        document_id=chunk.document_id,
                        filename=filename,
                        page_number=chunk.page_number,
                        bounding_box=chunk.bounding_box
                    )
                )
                
        return retrieved_chunks
