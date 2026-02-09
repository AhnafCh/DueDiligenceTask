from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.storage.db.database import get_db
from src.models.answer import (
    Answer,
    AnswerCreate,
    AnswerUpdate,
    AnswerConfirm,
    AnswerReject,
    AnswerFlagMissing,
)
from src.storage.db.models import AnswerModel
from src.services.review_service import ReviewService

router = APIRouter(tags=["answers"])


def run_generate_single_answer(question_id: str):
    """Worker function for single answer generation."""
    from src.storage.db.database import SessionLocal
    db = SessionLocal()
    try:
        service = AnswerService(db)
        service.generate_answer(question_id)
    finally:
        db.close()

@router.post("/generate-single-answer")
def generate_single_answer(
    question_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """Generate a single answer for a question."""
    background_tasks.add_task(run_generate_single_answer, str(question_id))
    
    return {
        "request_id": str(question_id),
        "status": "pending",
        "message": "Answer generation started in background"
    }


@router.post("/generate-all-answers")
def generate_all_answers(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> dict:
    """Generate all answers for a project."""
    # This would normally trigger a background task that iterates through questions
    # For now, we'll just return a success message as a stub for the bulk trigger
    return {
        "request_id": str(uuid4()),
        "status": "pending",
        "message": "Bulk answer generation (stub)"
    }


@router.get("/get-answer", response_model=Answer)
def get_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
) -> Answer:
    """Get answer details."""
    answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    return Answer.model_validate(answer)


@router.post("/update-answer", response_model=Answer)
def update_answer(
    answer_id: UUID,
    answer_update: AnswerUpdate,
    db: Session = Depends(get_db)
) -> Answer:
    """Update/override an answer manually."""
    service = ReviewService(db)
    try:
        if answer_update.text:
            return service.manual_update(str(answer_id), answer_update.text)
        return service.manual_update(str(answer_id), "") # Or handle empty
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/confirm-answer", response_model=Answer)
def confirm_answer(
    answer_id: UUID,
    confirm_data: AnswerConfirm,
    db: Session = Depends(get_db)
) -> Answer:
    """Confirm an AI-generated answer."""
    service = ReviewService(db)
    try:
        return service.confirm_answer(str(answer_id), confirm_data.comment)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reject-answer", response_model=Answer)
def reject_answer(
    answer_id: UUID,
    reject_data: AnswerReject,
    db: Session = Depends(get_db)
) -> Answer:
    """Reject an AI-generated answer."""
    service = ReviewService(db)
    try:
        return service.reject_answer(str(answer_id), reject_data.reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/flag-answer-missing", response_model=Answer)
def flag_missing_data(
    answer_id: UUID,
    flag_data: AnswerFlagMissing,
    db: Session = Depends(get_db)
) -> Answer:
    """Flag an answer as having missing data."""
    service = ReviewService(db)
    try:
        return service.flag_missing_data(str(answer_id), flag_data.missing_info)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{answer_id}/refine", response_model=Answer)
def refine_answer(
    answer_id: UUID,
    feedback: str,
    db: Session = Depends(get_db)
) -> Answer:
    """Refine answer using LangGraph HITL with feedback."""
    service = ReviewService(db)
    try:
        return service.refine_answer(str(answer_id), feedback)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{answer_id}/history")
def get_answer_history(
    answer_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get answer review history."""
    service = ReviewService(db)
    history = service.get_history(str(answer_id))
    return {
        "answer_id": str(answer_id),
        "history": history
    }


@router.get("/{answer_id}/trace")
def get_answer_trace(
    answer_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get LangGraph execution trace."""
    service = ReviewService(db)
    return service.get_trace(str(answer_id))
