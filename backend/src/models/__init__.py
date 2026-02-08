"""Models package initialization."""

from src.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
    ProjectStatus,
    ScopeType,
    Section,
    SectionCreate,
    Question,
    QuestionCreate,
)
from src.models.answer import (
    Answer,
    AnswerCreate,
    AnswerUpdate,
    AnswerStatus,
    Citation,
    AnswerConfirm,
    AnswerReject,
    AnswerFlagMissing,
)
from src.models.document import (
    Document,
    DocumentCreate,
    DocumentUpdate,
    DocumentStatus,
    Chunk,
    IndexStatus,
)
from src.models.evaluation import (
    Evaluation,
    EvaluationCreate,
    SimilarityMetrics,
    GroundTruth,
    GroundTruthCreate,
    EvaluationReport,
)

__all__ = [
    # Project models
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectDetail",
    "ProjectStatus",
    "ScopeType",
    "Section",
    "SectionCreate",
    "Question",
    "QuestionCreate",
    # Answer models
    "Answer",
    "AnswerCreate",
    "AnswerUpdate",
    "AnswerStatus",
    "Citation",
    "AnswerConfirm",
    "AnswerReject",
    "AnswerFlagMissing",
    # Document models
    "Document",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentStatus",
    "Chunk",
    "IndexStatus",
    # Evaluation models
    "Evaluation",
    "EvaluationCreate",
    "SimilarityMetrics",
    "GroundTruth",
    "GroundTruthCreate",
    "EvaluationReport",
]
