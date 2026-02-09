import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import pytest
from unittest.mock import MagicMock, patch
from src.services.agent.nodes.generate import generate_node, GeneratedResponse
from src.services.agent.nodes.hallucination import hallucination_node, HallucinationResult
from src.services.retrieval import RetrievedChunk

@pytest.fixture
def mock_llm_service():
    with patch("src.services.agent.nodes.generate.LLMService") as mock_gen, \
         patch("src.services.agent.nodes.hallucination.LLMService") as mock_hall:
        yield mock_gen, mock_hall

def test_generate_node_unanswerable(mock_llm_service):
    mock_gen, _ = mock_llm_service
    mock_instance = mock_gen.return_value
    
    # Mock LLM saying it's unanswerable
    mock_instance.generate_structured.return_value = GeneratedResponse(
        answer="I don't know.",
        is_answerable=False,
        confidence_score=0.1,
        cited_indices=[]
    )
    
    state = {
        "question": "What is the secret code?",
        "documents": [
            RetrievedChunk(id="1", text="Public info", score=0.9, document_id="doc1", filename="f1.pdf")
        ],
        "steps": []
    }
    
    result = generate_node(state)
    
    assert result["is_answerable"] is False
    assert "generate" in result["steps"]
    assert result["generation"] == "I don't know."

def test_generate_node_successful(mock_llm_service):
    mock_gen, _ = mock_llm_service
    mock_instance = mock_gen.return_value
    
    # Mock LLM providing a good answer
    mock_instance.generate_structured.return_value = GeneratedResponse(
        answer="The answer is 42. [1]",
        is_answerable=True,
        confidence_score=0.95,
        cited_indices=[1]
    )
    
    state = {
        "question": "What is the answer?",
        "documents": [
            RetrievedChunk(id="1", text="The answer is 42.", score=0.99, document_id="doc1", filename="f1.pdf")
        ],
        "steps": []
    }
    
    result = generate_node(state)
    
    assert result["is_answerable"] is True
    assert result["confidence_score"] == 0.95
    assert len(result["documents"]) == 1
    assert result["documents"][0].id == "1"

def test_hallucination_node_positive(mock_llm_service):
    _, mock_hall = mock_llm_service
    mock_instance = mock_hall.return_value
    
    # Mock LLM saying it's grounded
    mock_instance.generate_structured.return_value = HallucinationResult(binary_score="yes")
    
    state = {
        "generation": "The answer is 42.",
        "documents": [
            RetrievedChunk(id="1", text="The answer is 42.", score=0.99, document_id="doc1", filename="f1.pdf")
        ],
        "steps": [],
        "retries": 0
    }
    
    result = hallucination_node(state)
    
    assert result["is_answerable"] is True
    assert result["retries"] == 0

def test_hallucination_node_negative(mock_llm_service):
    _, mock_hall = mock_llm_service
    mock_instance = mock_hall.return_value
    
    # Mock LLM saying it's NOT grounded
    mock_instance.generate_structured.return_value = HallucinationResult(binary_score="no")
    
    state = {
        "generation": "The answer is 99.",
        "documents": [
            RetrievedChunk(id="1", text="The answer is 42.", score=0.99, document_id="doc1", filename="f1.pdf")
        ],
        "steps": [],
        "retries": 0
    }
    
    result = hallucination_node(state)
    
    assert result["is_answerable"] is False
    assert result["retries"] == 1
