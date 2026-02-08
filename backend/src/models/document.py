from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    UPLOADED = "UPLOADED"
    INDEXING = "INDEXING"
    READY = "READY"
    ERROR = "ERROR"


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., max_length=10)
    file_size: int = Field(..., gt=0)


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_path: str


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None


class Document(DocumentBase):
    """Complete document schema."""
    id: UUID = Field(default_factory=uuid4)
    file_path: str
    status: DocumentStatus = DocumentStatus.UPLOADED
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    chunk_count: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    indexed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChunkBase(BaseModel):
    """Base chunk schema."""
    text: str
    chunk_index: int = Field(..., ge=0)
    page_number: Optional[int] = None
    bounding_box: Optional[dict] = None


class Chunk(ChunkBase):
    """Complete chunk schema."""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    embedding_vector: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class IndexStatus(BaseModel):
    """Index status information."""
    total_documents: int
    indexed_documents: int
    total_chunks: int
    last_updated: Optional[datetime] = None
