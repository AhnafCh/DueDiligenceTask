import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from src.services.llm_service import LLMService
from ..state import AgentState
from src.services.retrieval import RetrievedChunk

logger = logging.getLogger(__name__)

class GeneratedResponse(BaseModel):
    """Answer with answerability flag and confidence."""
    answer: str = Field(description="The final answer to the question with [1], [2] style citations")
    is_answerable: bool = Field(description="Whether the question can be answered based on the documents")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    cited_indices: List[int] = Field(description="List of 1-based indices of documents cited in the answer")

def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Generates an answer based on the retrieved documents with structured citations.
    """
    logger.info("---GENERATE NODE---")
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        return {
            "generation": "I'm sorry, I couldn't find any relevant information to answer this question.",
            "is_answerable": False,
            "confidence_score": 0.0,
            "steps": state["steps"] + ["generate"]
        }

    # Format context with indices
    context_list = []
    for i, doc in enumerate(documents, 1):
        context_list.append(f"[{i}] Source: {doc.filename}\nContent: {doc.text}")
    context = "\n\n".join(context_list)

    # Handle feedback if present
    feedback = state.get("feedback")
    feedback_prompt = f"\n\nUSER FEEDBACK ON PREVIOUS ATTEMPT: {feedback}\nPlease incorporate this feedback into your revised answer. Use the context to address the feedback." if feedback else ""

    prompt = f"""You are a due diligence assistant. Use the following context to answer the question.
    
    CRITICAL RULES:
    1. Only use information from the context.
    2. Cite the documents using [1], [2] style indices in the text.
    3. If the answer is not in the context, say you don't know and set is_answerable to false.
    4. Provide a confidence score based on how explicitly the context answers the question.
    5. List which document indices you actually used in 'cited_indices'.
    {feedback_prompt}

    Question: {question} 
    
    Context: 
    {context} 
    """
    
    try:
        llm = LLMService()
        response = llm.generate_structured(prompt, GeneratedResponse)
        
        # Calculate a more dynamic confidence score if it's too generic
        # (Simplified: average of LLM score and retrieval relevance if we had distances)
        # For now, we trust the LLM score but cap it if no docs were relevant.
        
        return {
            "generation": response.answer,
            "is_answerable": response.is_answerable,
            "confidence_score": response.confidence_score,
            "documents": [documents[i-1] for i in response.cited_indices if 0 < i <= len(documents)],
            "steps": state["steps"] + ["generate"]
        }
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {
            "generation": "Error during answer generation.",
            "is_answerable": False,
            "confidence_score": 0.0,
            "steps": state["steps"] + ["generate"]
        }
