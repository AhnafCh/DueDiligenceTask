import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
    # Also add backend dir
    sys.path.append(str(Path(__file__).parent.parent))

import logging
from typing import List
from sqlalchemy.orm import Session
from src.storage.db.database import SessionLocal
from src.services.answer_service import AnswerService
from src.services.agent.graph import create_rag_graph
from src.services.agent.state import AgentState

# Configure basic logging to see the graph steps
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def chat():
    """
    Standalone terminal script to chat with the RAG agent.
    """
    print("="*60)
    print("Questionnaire RAG Agent - Terminal Test Chat")
    print("="*60)
    print("Type 'exit' or 'quit' to stop.")
    
    db = SessionLocal()
    graph = create_rag_graph()
    
    try:
        while True:
            question = input("\nUser: ")
            if question.lower() in ['exit', 'quit']:
                break
                
            print("\n--- Agent is thinking ---\n")
            
            # Initial state for arbitrary terminal question
            # We don't have a question_id/project_id here, but we can still run the graph
            state: AgentState = {
                "question": question,
                "project_id": "terminal-test",
                "document_ids": None, # Search all
                "documents": [],
                "generation": None,
                "is_answerable": True,
                "confidence_score": 0.0,
                "retries": 0,
                "max_retries": 1,
                "errors": [],
                "steps": []
            }
            
            final_state = graph.invoke(state)
            
            print("-" * 40)
            print(f"Nodes visited: {' -> '.join(final_state['steps'])}")
            print("-" * 40)
            print(f"\nAI Answer: {final_state['generation']}")
            
            if final_state['documents']:
                print("\nCitations:")
                for i, doc in enumerate(final_state['documents'], 1):
                    print(f"[{i}] {doc.filename} (Score: {doc.score:.4f})")
                    # print(f"    Content: {doc.text[:100]}...")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        db.close()

if __name__ == "__main__":
    chat()
