import logging
from typing import Dict, Any
from src.services.retrieval.hybrid import HybridRetrievalService
from src.storage.db.database import get_db
from ..state import AgentState

logger = logging.getLogger(__name__)

def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    Retrieves documents based on the question.
    """
    logger.info("---RETRIEVE NODE---")
    question = state["question"]
    document_ids = state.get("document_ids")
    
    # Get DB session
    db = next(get_db())
    retrieval_service = HybridRetrievalService(db)
    
    # Perform retrieval
    documents = retrieval_service.search(
        query=question, 
        k=5, 
        document_ids=document_ids
    )
    
    return {
        "documents": documents,
        "steps": state["steps"] + ["retrieve"]
    }
