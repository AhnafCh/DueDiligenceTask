"""Chunking configuration models."""
from pydantic import BaseModel, Field
from typing import Optional


class ChunkingConfig(BaseModel):
    """Configuration for text chunking."""
    
    chunk_size: int = Field(default=1000, ge=100, le=5000, description="Target size of each chunk in characters")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Overlap between consecutive chunks")
    min_chunk_size: int = Field(default=100, ge=50, description="Minimum chunk size to keep")
    separator: str = Field(default="\n\n", description="Primary separator for splitting text")
    
    class Config:
        frozen = True  # Make immutable


class DocumentTypeConfig(BaseModel):
    """Document type-specific chunking configurations."""
    
    pdf: ChunkingConfig = ChunkingConfig(chunk_size=1000, chunk_overlap=200)
    docx: ChunkingConfig = ChunkingConfig(chunk_size=1200, chunk_overlap=200)
    xlsx: ChunkingConfig = ChunkingConfig(chunk_size=800, chunk_overlap=100)
    pptx: ChunkingConfig = ChunkingConfig(chunk_size=600, chunk_overlap=100)
    
    def get_config(self, file_extension: str) -> ChunkingConfig:
        """Get configuration for specific file type."""
        ext = file_extension.lower().lstrip('.')
        return getattr(self, ext, self.pdf)
