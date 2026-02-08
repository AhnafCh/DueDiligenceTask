from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.storage.db.database import get_db
from src.models.evaluation import (
    Evaluation,
    EvaluationCreate,
    GroundTruth,
    GroundTruthCreate,
    EvaluationReport,
)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/compare", response_model=Evaluation)
def compare_answers(
    evaluation: EvaluationCreate,
    db: Session = Depends(get_db)
) -> Evaluation:
    """Compare AI answer with human ground truth."""
    # Stub implementation - will be implemented in Phase 6
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Evaluation comparison not yet implemented (Phase 6)"
    )


@router.get("/project/{project_id}", response_model=EvaluationReport)
def get_project_evaluation(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> EvaluationReport:
    """Get evaluation report for a project."""
    # Stub implementation - will be implemented in Phase 6
    return EvaluationReport(
        project_id=project_id,
        total_questions=0,
        evaluated_questions=0,
        average_semantic_similarity=0.0,
        average_keyword_overlap=0.0,
        average_combined_score=0.0,
        evaluations=[]
    )


@router.post("/ground-truth", response_model=GroundTruth)
def set_ground_truth(
    ground_truth: GroundTruthCreate,
    db: Session = Depends(get_db)
) -> GroundTruth:
    """Set ground truth answer for a question."""
    # Stub implementation - will be implemented in Phase 6
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ground truth storage not yet implemented (Phase 6)"
    )
