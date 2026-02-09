import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from src.storage.db.models import GroundTruthModel, EvaluationModel, AnswerModel, QuestionModel, ProjectModel
from src.models.evaluation import Evaluation, EvaluationCreate, GroundTruth, GroundTruthCreate, EvaluationReport
from src.services.evaluation.comparator import AnswerComparator
from src.services.evaluation.report import generate_report

logger = logging.getLogger(__name__)

class EvaluationService:
    """Service for managing ground truths and evaluating AI answers."""
    
    def __init__(self, db: Session):
        self.db = db
        self.comparator = AnswerComparator()

    def create_ground_truth(self, gt: GroundTruthCreate) -> GroundTruth:
        """Create or update a ground truth answer for a question."""
        logger.info(f"Creating ground truth for question {gt.question_id}")
        
        # Check if GT already exists for this question
        existing = self.db.query(GroundTruthModel).filter(
            GroundTruthModel.question_id == str(gt.question_id)
        ).first()
        
        if existing:
            existing.answer_text = gt.answer_text
            existing.source = gt.source
            db_gt = existing
        else:
            db_gt = GroundTruthModel(
                question_id=str(gt.question_id),
                answer_text=gt.answer_text,
                source=gt.source
            )
            self.db.add(db_gt)
            
        try:
            self.db.commit()
            self.db.refresh(db_gt)
            return GroundTruth.model_validate(db_gt)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create ground truth: {e}")
            raise

    def evaluate_answer(self, ai_answer_id: UUID, human_answer_text: Optional[str] = None) -> Evaluation:
        """Compare an AI answer against ground truth and store the evaluation."""
        logger.info(f"Evaluating AI answer {ai_answer_id}")
        
        # 1. Get AI Answer
        ai_answer = self.db.query(AnswerModel).filter(AnswerModel.id == str(ai_answer_id)).first()
        if not ai_answer:
            raise ValueError(f"AI Answer {ai_answer_id} not found")
            
        # 2. Get Question
        question = self.db.query(QuestionModel).filter(QuestionModel.id == ai_answer.question_id).first()
        if not question:
            raise ValueError(f"Question {ai_answer.question_id} not found")
            
        # 3. Get Ground Truth text
        if human_answer_text:
            ans_text = human_answer_text
        else:
            gt = self.db.query(GroundTruthModel).filter(GroundTruthModel.question_id == question.id).first()
            if not gt:
                raise ValueError(f"No ground truth found for question {question.id}")
            ans_text = gt.answer_text
            
        # 4. Perform comparison
        evaluation_result = self.comparator.compare_answers(
            question_text=question.text,
            ai_answer_text=ai_answer.text,
            human_answer_text=ans_text,
            ai_answer_id=ai_answer_id
        )
        
        # 5. Store in DB
        db_eval = EvaluationModel(
            ai_answer_id=str(ai_answer_id),
            human_answer_text=ans_text,
            semantic_similarity=evaluation_result.metrics.semantic_similarity,
            keyword_overlap=evaluation_result.metrics.keyword_overlap,
            bleu_score=evaluation_result.metrics.bleu_score,
            agentic_score=evaluation_result.metrics.agentic_score,
            combined_score=evaluation_result.metrics.combined_score,
            explanation=evaluation_result.metrics.explanation
        )
        
        self.db.add(db_eval)
        try:
            self.db.commit()
            self.db.refresh(db_eval)
            
            # Since Evaluation Pydantic model uses SimilarityMetrics nested, we map it
            return Evaluation(
                id=UUID(db_eval.id),
                ai_answer_id=UUID(db_eval.ai_answer_id),
                human_answer_text=db_eval.human_answer_text,
                metrics=evaluation_result.metrics,
                created_at=db_eval.created_at
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save evaluation: {e}")
            raise

    def get_project_report(self, project_id: UUID) -> EvaluationReport:
        """Generate an evaluation report for all evaluated questions in a project."""
        logger.info(f"Generating evaluation report for project {project_id}")
        
        # 1. Get all questions for project
        questions = self.db.query(QuestionModel).filter(QuestionModel.project_id == str(project_id)).all()
        
        # 2. Get all evaluations for these questions
        evaluations_db = self.db.query(EvaluationModel).join(
            AnswerModel, EvaluationModel.ai_answer_id == AnswerModel.id
        ).join(
            QuestionModel, AnswerModel.question_id == QuestionModel.id
        ).filter(
            QuestionModel.project_id == str(project_id)
        ).all()
        
        evals = []
        for e in evaluations_db:
            # Reconstruct Pydantic model
            from src.models.evaluation import SimilarityMetrics
            metrics = SimilarityMetrics(
                semantic_similarity=e.semantic_similarity,
                keyword_overlap=e.keyword_overlap,
                bleu_score=e.bleu_score,
                agentic_score=e.agentic_score,
                combined_score=e.combined_score,
                explanation=e.explanation
            )
            evals.append(Evaluation(
                id=UUID(e.id),
                ai_answer_id=UUID(e.ai_answer_id),
                human_answer_text=e.human_answer_text,
                metrics=metrics,
                created_at=e.created_at
            ))
        
        return generate_report(project_id, evals, len(questions))
