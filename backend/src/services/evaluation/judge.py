import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class JudgeResponse(BaseModel):
    """Structured response from the evaluation judge."""
    faithfulness_score: float = Field(description="Score based on factual alignment with ground truth (0-1)")
    relevance_score: float = Field(description="Score based on how well the question is answered (0-1)")
    conciseness_score: float = Field(description="Score based on brevity and directness (0-1)")
    overall_score: float = Field(description="Aggregated qualitative score (0-1)")
    explanation: str = Field(description="Detailed qualitative assessment")

class EvaluationJudge:
    """LLM-based judge for evaluating answer quality."""
    
    def __init__(self):
        self.llm = LLMService()
        
    def evaluate_answer(self, question: str, ai_answer: str, human_answer: str) -> JudgeResponse:
        """
        Evaluate AI answer against human answer using LLM-as-a-judge.
        """
        prompt = f"""You are an expert evaluator for a due diligence questionnaire system. 
        Your task is to compare an AI-generated answer with a human-provided ground truth answer for a given question.

        Criteria:
        1. Faithfulness: How well does the AI answer align with the factual content of the ground truth?
        2. Relevance: How well does the AI answer address the core question?
        3. Conciseness: Is the answer concise and to the point without losing essential information?

        Provide a score from 0.0 to 1.0 for each criterion and an overall score.
        Also provide a brief qualitative explanation for your scoring.

        Question: {question}
        AI Answer: {ai_answer}
        Ground Truth Answer: {human_answer}
        """

        try:
            return self.llm.generate_structured(prompt, JudgeResponse)
        except Exception as e:
            logger.error(f"Error in agentic evaluation: {e}")
            return JudgeResponse(
                faithfulness_score=0.0,
                relevance_score=0.0,
                conciseness_score=0.0,
                overall_score=0.0,
                explanation=f"Evaluation failed: {str(e)}"
            )
