import logging
from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.retrieval import retrieve_node
from .nodes.grade import grade_node
from .nodes.generate import generate_node
from .nodes.hallucination import hallucination_node

logger = logging.getLogger(__name__)

def decide_to_generate(state: AgentState):
    """
    Determines whether to generate an answer, or re-retrieve.
    """
    logger.info("---ASSESSING NEXT STEP---")
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We could add an "improve_query" step here.
        # For now, if no docs, we just try to generate with what we have (which will handle failure)
        logger.info("---DECISION: NO RELEVANT DOCUMENTS, ENDING---")
        return "generate"
    else:
        # We have relevant documents, so generate answer
        logger.info("---DECISION: GENERATE---")
        return "generate"

def grade_generation_v_documents_and_question(state: AgentState):
    """
    Determines whether the generation is grounded in the documents and answers question.
    """
    logger.info("---GRADING GENERATION---")
    is_grounded = state.get("is_answerable", True)
    
    if is_grounded:
        logger.info("---DECISION: GENERATION IS GROUNDED---")
        return "useful"
    else:
        logger.info("---DECISION: GENERATION IS NOT GROUNDED---")
        if state["retries"] < state["max_retries"]:
            return "not grounded"
        return "useful" # Give up and return what we have

def create_rag_graph():
    """
    Creates and compiles the LangGraph for RAG.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("hallucination_check", hallucination_node)

    # Build graph
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "generate": "generate",
        },
    )
    
    workflow.add_edge("generate", "hallucination_check")
    
    workflow.add_conditional_edges(
        "hallucination_check",
        grade_generation_v_documents_and_question,
        {
            "not grounded": "generate",
            "useful": END,
        },
    )

    return workflow.compile()
