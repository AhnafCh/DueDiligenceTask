from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class ProjectStatus(str, Enum):
    """Project lifecycle status."""
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    READY = "READY"
    REVIEW = "REVIEW"
    COMPLETED = "COMPLETED"
    OUTDATED = "OUTDATED"


class ScopeType(str, Enum):
    """Project scope type."""
    ALL_DOCS = "ALL_DOCS"
    SPECIFIC = "SPECIFIC"


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scope_type: ScopeType = ScopeType.ALL_DOCS


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    document_ids: Optional[List[UUID]] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scope_type: Optional[ScopeType] = None
    status: Optional[ProjectStatus] = None
    document_ids: Optional[List[UUID]] = None


class Project(ProjectBase):
    """Complete project schema."""
    id: UUID = Field(default_factory=uuid4)
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class SectionBase(BaseModel):
    """Base section schema."""
    title: str = Field(..., min_length=1, max_length=500)
    order: int = Field(..., ge=0)
    description: Optional[str] = None


class SectionCreate(SectionBase):
    """Schema for creating a section."""
    project_id: UUID


class Section(SectionBase):
    """Complete section schema."""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """Base question schema."""
    text: str = Field(..., min_length=1)
    order: int = Field(..., ge=0)
    expected_answer_type: Optional[str] = Field(None, max_length=50)


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    project_id: UUID
    section_id: Optional[UUID] = None


class Question(QuestionBase):
    """Complete question schema."""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    section_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ProjectDetail(Project):
    """Detailed project with sections and questions."""
    sections: List[Section] = Field(default_factory=list)
    questions: List[Question] = Field(default_factory=list)
    document_count: int = 0
