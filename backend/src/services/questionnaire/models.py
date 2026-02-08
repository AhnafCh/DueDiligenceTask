"""Intermediate models for questionnaire parsing."""
from typing import List, Optional
from pydantic import BaseModel, Field

class ParsedQuestion(BaseModel):
    """A single question extracted from the questionnaire."""
    text: str = Field(..., description="The question text")
    order: int = Field(..., description="The order of the question in the section")
    expected_answer_type: Optional[str] = Field(None, description="Expected type of answer (e.g., text, number, date)")

class ParsedSection(BaseModel):
    """A section of the questionnaire containing questions."""
    title: str = Field(..., description="Section title")
    order: int = Field(..., description="The order of the section")
    questions: List[ParsedQuestion] = Field(default_factory=list, description="List of questions in this section")

class ParsedQuestionnaire(BaseModel):
    """The structure of a parsed questionnaire."""
    sections: List[ParsedSection] = Field(default_factory=list, description="List of sections in the questionnaire")
