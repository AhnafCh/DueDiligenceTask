"""Text splitter for semantic chunking with metadata preservation."""
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import ChunkingConfig

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a text chunk."""
    chunk_index: int
    page_number: Optional[int] = None
    bounding_box: Optional[Dict[str, Any]] = None
    source_document: Optional[str] = None


@dataclass
class TextChunk:
    """A chunk of text with associated metadata."""
    text: str
    metadata: ChunkMetadata


class SemanticTextSplitter:
    """
    Semantic text splitter with configurable chunking strategy.
    
    Uses recursive character splitting to maintain semantic coherence
    while respecting chunk size limits.
    """
    
    def __init__(self, config: ChunkingConfig):
        """
        Initialize the text splitter.
        
        Args:
            config: Chunking configuration
        """
        self.config = config
        
        # Initialize LangChain text splitter with recursive strategy
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # Double newline (paragraphs)
                "\n",    # Single newline
                ". ",    # Sentence end
                ", ",    # Clause
                " ",     # Word
                ""       # Character
            ]
        )
    
    def split_text(
        self,
        text: str,
        page_number: Optional[int] = None,
        bounding_box: Optional[Dict[str, Any]] = None,
        source_document: Optional[str] = None
    ) -> List[TextChunk]:
        """
        Split text into semantic chunks with metadata.
        
        Args:
            text: Text to split
            page_number: Optional page number for the text
            bounding_box: Optional bounding box information
            source_document: Optional source document identifier
            
        Returns:
            List of TextChunk objects with metadata
        """
        if not text or not text.strip():
            return []
        
        # Split text using LangChain splitter
        text_chunks = self.splitter.split_text(text)
        
        # Create TextChunk objects with metadata
        chunks: List[TextChunk] = []
        for idx, chunk_text in enumerate(text_chunks):
            # Skip chunks that are too small
            if len(chunk_text.strip()) < self.config.min_chunk_size:
                logger.debug(f"Skipping chunk {idx} (too small: {len(chunk_text)} chars)")
                continue
            
            metadata = ChunkMetadata(
                chunk_index=idx,
                page_number=page_number,
                bounding_box=bounding_box,
                source_document=source_document
            )
            
            chunks.append(TextChunk(text=chunk_text.strip(), metadata=metadata))
        
        return chunks
    
    def split_by_pages(
        self,
        page_texts: List[str],
        bounding_boxes: Optional[List[Dict[str, Any]]] = None,
        source_document: Optional[str] = None
    ) -> List[TextChunk]:
        """
        Split multiple pages into chunks while preserving page numbers.
        
        Args:
            page_texts: List of text content per page
            bounding_boxes: Optional list of bounding boxes per page
            source_document: Optional source document identifier
            
        Returns:
            List of TextChunk objects with page metadata
        """
        all_chunks: List[TextChunk] = []
        global_chunk_index = 0
        
        for page_num, page_text in enumerate(page_texts, start=1):
            if not page_text or not page_text.strip():
                continue
            
            # Get bounding box for this page if available
            bbox = None
            if bounding_boxes and len(bounding_boxes) >= page_num:
                bbox = bounding_boxes[page_num - 1]
            
            # Split page text
            page_chunks = self.split_text(
                text=page_text,
                page_number=page_num,
                bounding_box=bbox,
                source_document=source_document
            )
            
            # Update global chunk indices
            for chunk in page_chunks:
                chunk.metadata.chunk_index = global_chunk_index
                global_chunk_index += 1
                all_chunks.append(chunk)
        
        return all_chunks
