import logging
from typing import Dict, Any, List
from uuid import UUID

from src.models.evaluation import SimilarityMetrics, Evaluation
from src.services.embedding_service import get_embedding_service
from .similarity import calculate_cosine_similarity, calculate_keyword_overlap, calculate_bleu_score
from .judge import EvaluationJudge

logger = logging.getLogger(__name__)

class AnswerComparator:
    """Service to compare AI answers with human ground truth."""
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.judge = EvaluationJudge()
        
    def compare_answers(
        self, 
        question_text: str, 
        ai_answer_text: str, 
        human_answer_text: str,
        ai_answer_id: UUID
    ) -> Evaluation:
        """
        Perform a full comparison between AI and human answers.
        """
        logger.info(f"Comparing AI answer {ai_answer_id} with human ground truth")
        
        # 1. Semantic Similarity
        try:
            ai_embedding = self.embedding_service.generate_embedding(ai_answer_text)
            human_embedding = self.embedding_service.generate_embedding(human_answer_text)
            semantic_sim = calculate_cosine_similarity(ai_embedding, human_embedding)
        except Exception as e:
            logger.error(f"Failed to calculate semantic similarity: {e}")
            semantic_sim = 0.0
            
        # 2. Keyword Overlap
        keyword_overlap = calculate_keyword_overlap(ai_answer_text, human_answer_text)
        
        # 3. BLEU Score
        bleu = calculate_bleu_score(human_answer_text, ai_answer_text)
        
        # 4. Agentic Evaluation (LLM Judge)
        judge_result = self.judge.evaluate_answer(question_text, ai_answer_text, human_answer_text)
        
        # 5. Combined Score
        # Weighting: 40% Semantic, 20% Keyword, 10% BLEU, 30% Judge
        combined = (
            (semantic_sim * 0.4) + 
            (keyword_overlap * 0.2) + 
            (bleu * 0.1) + 
            (judge_result.overall_score * 0.3)
        )
        
        metrics = SimilarityMetrics(
            semantic_similarity=semantic_sim,
            keyword_overlap=keyword_overlap,
            bleu_score=bleu,
            agentic_score=judge_result.overall_score,
            combined_score=combined,
            explanation=judge_result.explanation
        )
        
        return Evaluation(
            ai_answer_id=ai_answer_id,
            human_answer_text=human_answer_text,
            metrics=metrics
        )
