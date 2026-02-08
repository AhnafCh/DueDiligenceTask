import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.services.llm_service import LLMService
from ..state import AgentState

logger = logging.getLogger(__name__)

class GradeResult(BaseModel):
    """Binary score for relevance check."""
    binary_score: str = Field(description="Relevance score 'yes' or 'no'")

def grade_node(state: AgentState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question.
    """
    logger.info("---CHECK RELEVANCE NODE---")
    question = state["question"]
    documents = state["documents"]
    
    llm = LLMService()
    
    filtered_docs = []
    for doc in documents:
        prompt = f"""You are a grader assessing relevance of a retrieved document to a user question. 
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. 
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        
        Retrieved document: 
        {doc.text}
        
        User question: {question}
        """
        
        result = llm.generate_structured(prompt, GradeResult)
        if result.binary_score.lower() == "yes":
            logger.info("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(doc)
        else:
            logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
            
    return {
        "documents": filtered_docs,
        "steps": state["steps"] + ["grade_documents"]
    }
