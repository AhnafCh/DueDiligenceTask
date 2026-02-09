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
from src.services.evaluation_service import EvaluationService

router = APIRouter(tags=["evaluation"])


@router.post("/compare", response_model=Evaluation)
def compare_answers(
    evaluation: EvaluationCreate,
    db: Session = Depends(get_db)
) -> Evaluation:
    """Compare AI answer with human ground truth."""
    service = EvaluationService(db)
    try:
        return service.evaluate_answer(
            evaluation.ai_answer_id, 
            evaluation.human_answer_text
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/get-project-evaluation", response_model=EvaluationReport)
def get_project_evaluation(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> EvaluationReport:
    """Get evaluation report for a project."""
    service = EvaluationService(db)
    try:
        return service.get_project_report(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.post("/ground-truth", response_model=GroundTruth)
def set_ground_truth(
    ground_truth: GroundTruthCreate,
    db: Session = Depends(get_db)
) -> GroundTruth:
    """Set ground truth answer for a question."""
    service = EvaluationService(db)
    try:
        return service.create_ground_truth(ground_truth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set ground truth: {str(e)}")
