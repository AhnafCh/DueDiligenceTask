import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.services.llm_service import LLMService
from ..state import AgentState

logger = logging.getLogger(__name__)

class HallucinationResult(BaseModel):
    """Binary score for hallucination check."""
    binary_score: str = Field(description="Answer is grounded in the documents, 'yes' or 'no'")

def hallucination_node(state: AgentState) -> Dict[str, Any]:
    """
    Determines whether the generation is grounded in the retrieved documents.
    """
    logger.info("---CHECK HALLUCINATIONS NODE---")
    generation = state["generation"]
    documents = state["documents"]
    
    if not generation or not documents:
        return {
            "steps": state["steps"] + ["check_hallucinations"],
            "is_answerable": True # "I don't know" is grounded in no context
        }

    context = "\n\n".join([doc.text for doc in documents])
    
    llm = LLMService()
    prompt = f"""You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved documents. 
    Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of documents.
    
    Retrieved documents: 
    {context}
    
    LLM generation: {generation}
    """
    
    result = llm.generate_structured(prompt, HallucinationResult)
    is_answerable = result.binary_score.lower() == "yes"
    
    return {
        "steps": state["steps"] + ["check_hallucinations"],
        "is_answerable": is_answerable,
        "retries": state["retries"] + (0 if is_answerable else 1)
    }
