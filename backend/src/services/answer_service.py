import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from datetime import datetime

from src.services.agent.graph import create_rag_graph
from src.services.agent.state import AgentState
from src.storage.db.models import AnswerModel, CitationModel, QuestionModel, ProjectModel
from src.models.answer import AnswerStatus

logger = logging.getLogger(__name__)

class AnswerService:
    """
    Main service for coordinating answer generation.
    Orchestrates the LangGraph agent and persists results.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.graph = create_rag_graph()

    def generate_answer(self, question_id: str) -> AnswerModel:
        """
        Generates an answer for a single question with persistence.
        """
        logger.info(f"Generating answer for question: {question_id}")
        
        # 1. Fetch question and project context
        question = self.db.query(QuestionModel).filter(QuestionModel.id == question_id).first()
        if not question:
            raise ValueError(f"Question {question_id} not found")
            
        project = self.db.query(ProjectModel).filter(ProjectModel.id == question.project_id).first()
        document_ids = [doc.id for doc in project.documents] if project and project.documents else None

        # 2. Prepare Agent State
        initial_state: AgentState = {
            "question": question.text,
            "project_id": str(question.project_id),
            "document_ids": document_ids,
            "documents": [],
            "generation": None,
            "is_answerable": True,
            "confidence_score": 0.0,
            "retries": 0,
            "max_retries": 1,
            "errors": [],
            "steps": [],
            "feedback": None
        }

        # 3. Run Agent with checkpointer
        from src.services.langgraph_persistence import LangGraphPersistence
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        with LangGraphPersistence.get_sqlite_checkpointer() as checkpointer:
            graph = create_rag_graph(checkpointer=checkpointer)
            final_state = graph.invoke(initial_state, config=config)

        # 4. Save to DB
        db_answer = AnswerModel(
            question_id=question_id,
            text=final_state["generation"] or "No answer generated.",
            is_answerable=final_state["is_answerable"],
            confidence_score=final_state["confidence_score"],
            status=AnswerStatus.PENDING,
            created_by="AI",
            thread_id=thread_id,
            processing_metadata={"steps": final_state.get("steps", [])},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_answer)
        self.db.flush()

        # 5. Save Citations
        from dataclasses import asdict, is_dataclass
        for doc in final_state.get("documents", []):
            bbox = doc.bounding_box
            if bbox and is_dataclass(bbox):
                bbox = asdict(bbox)
                
            citation = CitationModel(
                answer_id=db_answer.id,
                chunk_id=doc.id,
                chunk_text=doc.text,
                page_number=doc.page_number,
                bounding_box=bbox,
                document_name=doc.filename
            )
            self.db.add(citation)

        self.db.commit()
        self.db.refresh(db_answer)
        
        return db_answer

    def generate_all_for_project(self, project_id: str):
        """
        Trigger async generation for all questions in a project.
        (This will be called by a Celery task).
        """
        questions = self.db.query(QuestionModel).filter(QuestionModel.id == project_id).all()
        for q in questions:
            try:
                self.generate_answer(q.id)
            except Exception as e:
                logger.error(f"Failed to generate answer for {q.id}: {e}")
