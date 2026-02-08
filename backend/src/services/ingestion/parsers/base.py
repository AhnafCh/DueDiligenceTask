"""Base parser interface for document parsing."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class BoundingBox:
    """Bounding box coordinates for text elements."""
    x0: float
    y0: float
    x1: float
    y1: float
    page: int


@dataclass
class ParsedContent:
    """Structured result from document parsing."""
    text: str
    page_count: int
    metadata: Dict[str, Any]
    page_texts: List[str]  # Text per page
    bounding_boxes: Optional[List[BoundingBox]] = None


class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedContent:
        """
        Parse a document and extract structured content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ParsedContent with extracted text and metadata
            
        Raises:
            ValueError: If file format is invalid or unsupported
            IOError: If file cannot be read
        """
        pass
    
    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """
        Check if this parser supports the given file extension.
        
        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            True if supported, False otherwise
        """
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        return text.strip()
    
    def extract_metadata(self, **kwargs) -> Dict[str, Any]:
        """
        Extract common metadata fields.
        
        Returns:
            Dictionary of metadata
        """
        return {
            "parser": self.__class__.__name__,
            **kwargs
        }
