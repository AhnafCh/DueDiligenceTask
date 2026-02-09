import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from src.storage.db.models import AnswerModel, CitationModel, QuestionModel
from src.models.answer import AnswerStatus
from src.services.agent.graph import create_rag_graph
from src.services.langgraph_persistence import LangGraphPersistence

logger = logging.getLogger(__name__)

class ReviewService:
    """
    Handles answer review workflows and refinement.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def confirm_answer(self, answer_id: str, comment: Optional[str] = None) -> AnswerModel:
        """Approve an AI-generated answer."""
        answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not answer:
            raise ValueError(f"Answer {answer_id} not found")
        
        answer.status = AnswerStatus.CONFIRMED
        if comment:
            answer.review_comment = comment
        answer.updated_at = datetime.utcnow()
        
        self.db.commit()
        return answer

    def reject_answer(self, answer_id: str, reason: str) -> AnswerModel:
        """Reject an AI-generated answer with a reason."""
        answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not answer:
            raise ValueError(f"Answer {answer_id} not found")
        
        answer.status = AnswerStatus.REJECTED
        answer.review_comment = reason
        answer.updated_at = datetime.utcnow()
        
        self.db.commit()
        return answer

    def manual_update(self, answer_id: str, text: str) -> AnswerModel:
        """Manually override an answer while preserving the original AI answer."""
        ai_answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not ai_answer:
            raise ValueError(f"Answer {answer_id} not found")
        
        # Check if a human answer already exists for this question
        human_answer = self.db.query(AnswerModel).filter(
            AnswerModel.question_id == ai_answer.question_id,
            AnswerModel.created_by == "HUMAN"
        ).first()
        
        if human_answer:
            human_answer.text = text
            human_answer.status = AnswerStatus.MANUAL_UPDATED
            human_answer.updated_at = datetime.utcnow()
        else:
            human_answer = AnswerModel(
                question_id=ai_answer.question_id,
                text=text,
                status=AnswerStatus.MANUAL_UPDATED,
                created_by="HUMAN",
                is_answerable=True,
                confidence_score=1.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(human_answer)
        
        self.db.commit()
        self.db.refresh(human_answer)
        return human_answer

    def flag_missing_data(self, answer_id: str, missing_info: str) -> AnswerModel:
        """Flag an answer as having missing data in source docs."""
        answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not answer:
            raise ValueError(f"Answer {answer_id} not found")
        
        answer.status = AnswerStatus.MISSING_DATA
        answer.review_comment = f"MISSING DATA: {missing_info}"
        answer.updated_at = datetime.utcnow()
        
        self.db.commit()
        return answer

    def refine_answer(self, answer_id: str, feedback: str) -> AnswerModel:
        """
        Interactively refine an answer using LangGraph HITL via checkpointer.
        """
        db_answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not db_answer:
            raise ValueError(f"Answer {answer_id} not found")
        
        if not db_answer.thread_id:
            # If no thread_id, we can't refine easily with HITL, so we just restart or error
            # For now, let's assume we always have thread_id or we create one
            db_answer.thread_id = str(db_answer.id)
        
        thread_id = db_answer.thread_id
        config = {"configurable": {"thread_id": thread_id}}
        
        # 1. Get checkpointer and graph
        with LangGraphPersistence.get_sqlite_checkpointer() as checkpointer:
            graph = create_rag_graph(checkpointer=checkpointer)
            
            # 2. Add feedback to state and run again
            # We use 'update_state' to inject feedback into the thread
            # Or just 'invoke' with the feedback if the graph is designed to handle it
            graph.update_state(config, {"feedback": feedback})
            
            # 3. Resume the graph from the generation node (or wherever it makes sense)
            # Actually, we can just run it again, and it will pick up from the last checkpoint
            # and hopefully our nodes check for feedback.
            final_state = graph.invoke(None, config=config)
            
            # 4. Update the answer in DB
            db_answer.text = final_state["generation"] or db_answer.text
            db_answer.is_answerable = final_state["is_answerable"]
            db_answer.confidence_score = final_state["confidence_score"]
            db_answer.processing_metadata = {"steps": final_state.get("steps", [])}
            db_answer.updated_at = datetime.utcnow()
            
            # Clear old citations and add new ones if they changed
            # (Simplified: just add new ones, might want to deduplicate)
            # In a real app we'd delete old citations for this answer
            self.db.query(CitationModel).filter(CitationModel.answer_id == db_answer.id).delete()
            
            for doc in final_state.get("documents", []):
                citation = CitationModel(
                    answer_id=db_answer.id,
                    chunk_id=doc.id,
                    chunk_text=doc.text,
                    page_number=doc.page_number,
                    bounding_box=doc.bounding_box,
                    document_name=doc.filename
                )
                self.db.add(citation)
            
            self.db.commit()
            self.db.refresh(db_answer)
            
        return db_answer

    def get_history(self, answer_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for an answer."""
        # In a real app, we'd have a separate AuditLog table
        # For this task, we'll return the current state and comments
        answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not answer:
            return []
            
        return [
            {
                "timestamp": answer.created_at.isoformat(),
                "action": "GENERATED",
                "status": "PENDING",
                "created_by": "AI"
            },
            {
                "timestamp": answer.updated_at.isoformat(),
                "action": "UPDATED",
                "status": answer.status,
                "created_by": answer.created_by,
                "comment": answer.review_comment
            }
        ]

    def get_trace(self, answer_id: str) -> Dict[str, Any]:
        """Get processing trace for an answer."""
        answer = self.db.query(AnswerModel).filter(AnswerModel.id == answer_id).first()
        if not answer:
            return {}
        
        return {
            "thread_id": answer.thread_id,
            "steps": answer.processing_metadata.get("steps", []) if answer.processing_metadata else [],
            "metadata": answer.processing_metadata
        }
