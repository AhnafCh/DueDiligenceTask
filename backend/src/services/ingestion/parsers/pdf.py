"""PDF document parser using PyPDF2."""
import logging
from pathlib import Path
from typing import List, Optional
import PyPDF2
from PyPDF2 import PdfReader

from .base import BaseParser, ParsedContent, BoundingBox

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF documents."""
    
    def supports(self, file_extension: str) -> bool:
        """Check if file extension is .pdf"""
        return file_extension.lower() == ".pdf"
    
    def parse(self, file_path: Path) -> ParsedContent:
        """
        Parse PDF document and extract text with metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            ParsedContent with extracted text and metadata
            
        Raises:
            ValueError: If PDF is invalid or encrypted
            IOError: If file cannot be read
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    raise ValueError(f"PDF file is encrypted: {file_path}")
                
                page_count = len(reader.pages)
                page_texts: List[str] = []
                bounding_boxes: List[BoundingBox] = []
                
                # Extract text from each page
                for page_num, page in enumerate(reader.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        cleaned_text = self.clean_text(page_text)
                        page_texts.append(cleaned_text)
                        
                        # Try to extract bounding boxes if available
                        # Note: PyPDF2 has limited bbox support, this is a basic implementation
                        try:
                            if hasattr(page, 'mediabox'):
                                mediabox = page.mediabox
                                bbox = BoundingBox(
                                    x0=float(mediabox.lower_left[0]),
                                    y0=float(mediabox.lower_left[1]),
                                    x1=float(mediabox.upper_right[0]),
                                    y1=float(mediabox.upper_right[1]),
                                    page=page_num
                                )
                                bounding_boxes.append(bbox)
                        except Exception as e:
                            logger.debug(f"Could not extract bbox for page {page_num}: {e}")
                            
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        page_texts.append("")
                
                # Combine all page texts
                full_text = "\n\n".join(page_texts)
                
                # Extract metadata
                metadata = self.extract_metadata(
                    page_count=page_count,
                    file_size=file_path.stat().st_size,
                    file_name=file_path.name
                )
                
                # Add PDF-specific metadata if available
                if reader.metadata:
                    try:
                        if reader.metadata.title:
                            metadata['title'] = reader.metadata.title
                        if reader.metadata.author:
                            metadata['author'] = reader.metadata.author
                        if reader.metadata.creator:
                            metadata['creator'] = reader.metadata.creator
                        if reader.metadata.creation_date:
                            metadata['creation_date'] = str(reader.metadata.creation_date)
                    except Exception as e:
                        logger.debug(f"Could not extract PDF metadata: {e}")
                
                return ParsedContent(
                    text=full_text,
                    page_count=page_count,
                    metadata=metadata,
                    page_texts=page_texts,
                    bounding_boxes=bounding_boxes if bounding_boxes else None
                )
                
        except PyPDF2.errors.PdfReadError as e:
            raise ValueError(f"Invalid or corrupted PDF file: {e}")
        except FileNotFoundError:
            raise IOError(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise IOError(f"Failed to parse PDF: {e}")
