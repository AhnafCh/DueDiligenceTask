from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Table, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from src.storage.db.database import Base
from src.models.project import ProjectStatus, ScopeType
from src.models.answer import AnswerStatus
from src.models.document import DocumentStatus


# Association table for many-to-many relationship between projects and documents
project_documents = Table(
    'project_documents',
    Base.metadata,
    Column('project_id', String(36), ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('document_id', String(36), ForeignKey('documents.id', ondelete='CASCADE'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)


class ProjectModel(Base):
    """SQLAlchemy model for Project."""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    scope_type = Column(Enum(ScopeType), nullable=False, default=ScopeType.ALL_DOCS)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    sections = relationship("SectionModel", back_populates="project", cascade="all, delete-orphan")
    questions = relationship("QuestionModel", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", secondary=project_documents, back_populates="projects")


class SectionModel(Base):
    """SQLAlchemy model for Section."""
    __tablename__ = "sections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("ProjectModel", back_populates="sections")
    questions = relationship("QuestionModel", back_populates="section", cascade="all, delete-orphan")


class QuestionModel(Base):
    """SQLAlchemy model for Question."""
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = Column(String(36), ForeignKey('sections.id', ondelete='SET NULL'), nullable=True, index=True)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    expected_answer_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("ProjectModel", back_populates="questions")
    section = relationship("SectionModel", back_populates="questions")
    answers = relationship("AnswerModel", back_populates="question", cascade="all, delete-orphan")


class AnswerModel(Base):
    """SQLAlchemy model for Answer."""
    __tablename__ = "answers"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    text = Column(Text, nullable=False)
    is_answerable = Column(Boolean, default=True, nullable=False)
    confidence_score = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    status = Column(Enum(AnswerStatus), nullable=False, default=AnswerStatus.PENDING, index=True)
    created_by = Column(String(10), nullable=False, default="AI")  # "AI" or "HUMAN"
    review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("QuestionModel", back_populates="answers")
    citations = relationship("CitationModel", back_populates="answer", cascade="all, delete-orphan")


class CitationModel(Base):
    """SQLAlchemy model for Citation."""
    __tablename__ = "citations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    answer_id = Column(String(36), ForeignKey('answers.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_id = Column(String(36), ForeignKey('chunks.id', ondelete='CASCADE'), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    document_name = Column(String(255), nullable=True)
    
    # Relationships
    answer = relationship("AnswerModel", back_populates="citations")
    chunk = relationship("ChunkModel", back_populates="citations")


class DocumentModel(Base):
    """SQLAlchemy model for Document."""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False, index=True)
    file_type = Column(String(10), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED, index=True)
    error_message = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    indexed_at = Column(DateTime, nullable=True)
    
    # Relationships
    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")
    projects = relationship("ProjectModel", secondary=project_documents, back_populates="documents")


class ChunkModel(Base):
    """SQLAlchemy model for Chunk."""
    __tablename__ = "chunks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("DocumentModel", back_populates="chunks")
    citations = relationship("CitationModel", back_populates="chunk", cascade="all, delete-orphan")


class GroundTruthModel(Base):
    """SQLAlchemy model for Ground Truth answers."""
    __tablename__ = "ground_truths"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True, unique=True)
    answer_text = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EvaluationModel(Base):
    """SQLAlchemy model for Evaluation."""
    __tablename__ = "evaluations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_answer_id = Column(String(36), ForeignKey('answers.id', ondelete='CASCADE'), nullable=False, index=True)
    human_answer_text = Column(Text, nullable=False)
    semantic_similarity = Column(Float, nullable=False)
    keyword_overlap = Column(Float, nullable=False)
    bleu_score = Column(Float, nullable=False)
    combined_score = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
