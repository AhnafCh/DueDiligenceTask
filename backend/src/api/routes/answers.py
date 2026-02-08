from fastapi import APIRouter, Depends, HTTPException, status
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

router = APIRouter(prefix="/answers", tags=["answers"])


@router.post("/generate-single")
def generate_single_answer(
    question_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Generate a single answer for a question."""
    # Stub implementation - will be implemented in Phase 4
    return {
        "request_id": str(UUID("00000000-0000-0000-0000-000000000000")),
        "status": "pending",
        "message": "Answer generation queued (stub)"
    }


@router.post("/generate-all")
def generate_all_answers(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Generate all answers for a project."""
    # Stub implementation - will be implemented in Phase 4
    return {
        "request_id": str(UUID("00000000-0000-0000-0000-000000000000")),
        "status": "pending",
        "message": "Bulk answer generation queued (stub)"
    }


@router.get("/{answer_id}", response_model=Answer)
def get_answer(
    answer_id: UUID,
    db: Session = Depends(get_db)
) -> Answer:
    """Get answer details."""
    # Stub implementation
    answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    return Answer.model_validate(answer)


@router.put("/{answer_id}", response_model=Answer)
def update_answer(
    answer_id: UUID,
    answer_update: AnswerUpdate,
    db: Session = Depends(get_db)
) -> Answer:
    """Update/override an answer."""
    # Stub implementation
    db_answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not db_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    update_data = answer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "is_manual" and value:
            db_answer.created_by = "HUMAN"
        else:
            setattr(db_answer, field, value)
    
    db.commit()
    db.refresh(db_answer)
    
    return Answer.model_validate(db_answer)


@router.post("/{answer_id}/confirm", response_model=Answer)
def confirm_answer(
    answer_id: UUID,
    confirm_data: AnswerConfirm,
    db: Session = Depends(get_db)
) -> Answer:
    """Confirm an AI-generated answer."""
    # Stub implementation
    db_answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not db_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    from src.models.answer import AnswerStatus
    db_answer.status = AnswerStatus.CONFIRMED
    if confirm_data.comment:
        db_answer.review_comment = confirm_data.comment
    
    db.commit()
    db.refresh(db_answer)
    
    return Answer.model_validate(db_answer)


@router.post("/{answer_id}/reject", response_model=Answer)
def reject_answer(
    answer_id: UUID,
    reject_data: AnswerReject,
    db: Session = Depends(get_db)
) -> Answer:
    """Reject an AI-generated answer."""
    # Stub implementation
    db_answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not db_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    from src.models.answer import AnswerStatus
    db_answer.status = AnswerStatus.REJECTED
    db_answer.review_comment = reject_data.reason
    
    db.commit()
    db.refresh(db_answer)
    
    return Answer.model_validate(db_answer)


@router.post("/{answer_id}/flag-missing", response_model=Answer)
def flag_missing_data(
    answer_id: UUID,
    flag_data: AnswerFlagMissing,
    db: Session = Depends(get_db)
) -> Answer:
    """Flag an answer as having missing data."""
    # Stub implementation
    db_answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not db_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    from src.models.answer import AnswerStatus
    db_answer.status = AnswerStatus.MISSING_DATA
    db_answer.review_comment = flag_data.missing_info
    
    db.commit()
    db.refresh(db_answer)
    
    return Answer.model_validate(db_answer)


@router.get("/{answer_id}/history")
def get_answer_history(
    answer_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get answer review history."""
    # Stub implementation - will be fully implemented in Phase 5
    db_answer = db.query(AnswerModel).filter(AnswerModel.id == str(answer_id)).first()
    if not db_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer {answer_id} not found"
        )
    
    return {
        "answer_id": str(db_answer.id),
        "history": [
            {
                "timestamp": db_answer.created_at.isoformat(),
                "action": "created",
                "status": db_answer.status,
                "comment": db_answer.review_comment
            }
        ]
    }
