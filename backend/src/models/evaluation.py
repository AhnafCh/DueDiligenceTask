from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class SimilarityMetrics(BaseModel):
    """Similarity metrics for evaluation."""
    semantic_similarity: float = Field(..., ge=0.0, le=1.0)
    keyword_overlap: float = Field(..., ge=0.0, le=1.0)
    bleu_score: float = Field(..., ge=0.0, le=1.0)
    combined_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class EvaluationBase(BaseModel):
    """Base evaluation schema."""
    ai_answer_id: UUID
    human_answer_text: str


class EvaluationCreate(EvaluationBase):
    """Schema for creating an evaluation."""
    pass


class Evaluation(EvaluationBase):
    """Complete evaluation schema."""
    id: UUID = Field(default_factory=uuid4)
    metrics: SimilarityMetrics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class GroundTruthBase(BaseModel):
    """Base ground truth schema."""
    question_id: UUID
    answer_text: str
    source: Optional[str] = None


class GroundTruthCreate(GroundTruthBase):
    """Schema for creating ground truth."""
    pass


class GroundTruth(GroundTruthBase):
    """Complete ground truth schema."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class EvaluationReport(BaseModel):
    """Evaluation report for a project."""
    project_id: UUID
    total_questions: int
    evaluated_questions: int
    average_semantic_similarity: float
    average_keyword_overlap: float
    average_combined_score: float
    evaluations: list[Evaluation] = Field(default_factory=list)
