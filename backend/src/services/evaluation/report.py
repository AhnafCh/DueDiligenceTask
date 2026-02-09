from typing import List
from uuid import UUID
from src.models.evaluation import Evaluation, EvaluationReport

def generate_report(project_id: UUID, evaluations: List[Evaluation], total_questions: int) -> EvaluationReport:
    """
    Generate a summary report for a project's evaluations.
    """
    if not evaluations:
        return EvaluationReport(
            project_id=project_id,
            total_questions=total_questions,
            evaluated_questions=0,
            average_semantic_similarity=0.0,
            average_keyword_overlap=0.0,
            average_combined_score=0.0,
            evaluations=[]
        )
    
    avg_semantic = sum(e.metrics.semantic_similarity for e in evaluations) / len(evaluations)
    avg_keyword = sum(e.metrics.keyword_overlap for e in evaluations) / len(evaluations)
    avg_combined = sum(e.metrics.combined_score for e in evaluations) / len(evaluations)
    
    return EvaluationReport(
        project_id=project_id,
        total_questions=total_questions,
        evaluated_questions=len(evaluations),
        average_semantic_similarity=avg_semantic,
        average_keyword_overlap=avg_keyword,
        average_combined_score=avg_combined,
        evaluations=evaluations
    )
