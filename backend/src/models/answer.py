from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class AnswerStatus(str, Enum):
    """Answer review status."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    MANUAL_UPDATED = "MANUAL_UPDATED"
    MISSING_DATA = "MISSING_DATA"


class CitationBase(BaseModel):
    """Base citation schema."""
    chunk_text: str
    page_number: Optional[int] = None
    bounding_box: Optional[dict] = None
    document_name: Optional[str] = None


class Citation(CitationBase):
    """Complete citation schema."""
    id: UUID = Field(default_factory=uuid4)
    answer_id: UUID
    chunk_id: UUID
    
    class Config:
        from_attributes = True


class AnswerBase(BaseModel):
    """Base answer schema."""
    text: str
    is_answerable: bool = True
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    explanation: Optional[str] = None


class AnswerCreate(AnswerBase):
    """Schema for creating an answer."""
    question_id: UUID
    citations: Optional[List[CitationBase]] = Field(default_factory=list)


class AnswerUpdate(BaseModel):
    """Schema for updating an answer."""
    text: Optional[str] = None
    status: Optional[AnswerStatus] = None
    review_comment: Optional[str] = None
    is_manual: bool = False


class Answer(AnswerBase):
    """Complete answer schema."""
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    status: AnswerStatus = AnswerStatus.PENDING
    created_by: str = "AI"  # "AI" or "HUMAN"
    review_comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    citations: List[Citation] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class AnswerConfirm(BaseModel):
    """Schema for confirming an answer."""
    comment: Optional[str] = None


class AnswerReject(BaseModel):
    """Schema for rejecting an answer."""
    reason: str = Field(..., min_length=1)


class AnswerFlagMissing(BaseModel):
    """Schema for flagging missing data."""
    missing_info: str = Field(..., min_length=1)
