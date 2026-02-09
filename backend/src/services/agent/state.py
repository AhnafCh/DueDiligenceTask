from typing import List, TypedDict, Optional, Dict, Any
from src.services.retrieval import RetrievedChunk

class AgentState(TypedDict):
    """
    Represents the state of our LangGraph agent.
    """
    question: str
    project_id: str
    document_ids: Optional[List[str]]  # Restricted scope if applicable
    documents: List[RetrievedChunk]
    generation: Optional[str]
    is_answerable: bool
    confidence_score: float
    retries: int
    max_retries: int
    errors: List[str]
    # Trace metadata
    steps: List[str]
    feedback: Optional[str]
