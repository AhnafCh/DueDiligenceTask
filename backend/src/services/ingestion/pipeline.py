"""Ingestion Pipeline Service."""
import logging
import traceback
from pathlib import Path
from sqlalchemy.orm import Session

from src.models.document import DocumentStatus
from src.services.document_service import DocumentService
from src.services.ingestion.parsers.pdf import PDFParser
from src.services.ingestion.parsers.docx import DOCXParser
from src.services.ingestion.parsers.xlsx import XLSXParser
from src.services.ingestion.parsers.pptx import PPTXParser
from src.services.ingestion.chunking.splitter import SemanticTextSplitter
from src.services.ingestion.chunking.config import DocumentTypeConfig
from src.indexing.manager import IndexManager
from src.storage.db.models import ChunkModel, DocumentModel

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    End-to-end document ingestion pipeline.
    Parses -> Chunks -> Embeds -> Indexes.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.document_service = DocumentService(db)
        self.index_manager = IndexManager()
        self.chunk_config = DocumentTypeConfig()
        
        # Initialize parsers
        self.parsers = [
            PDFParser(),
            DOCXParser(),
            XLSXParser(),
            PPTXParser()
        ]

    def _get_parser(self, file_path: Path):
        """Find appropriate parser for file."""
        ext = file_path.suffix
        for parser in self.parsers:
            if parser.supports(ext):
                return parser
        raise ValueError(f"No parser found for extension: {ext}")

    def run(self, document_id: str):
        """
        Run ingestion pipeline for a document.
        
        Args:
            document_id: ID of the document to process
        """
        doc = self.document_service.get_document(document_id)
        if not doc:
            logger.error(f"Document {document_id} not found")
            return
            
        try:
            # 1. Update status to INDEXING
            self.document_service.update_status(document_id, DocumentStatus.INDEXING)
            logger.info(f"Starting ingestion for document {doc.filename}")
            
            # 2. Parse Document
            file_path = Path(doc.file_path)
            parser = self._get_parser(file_path)
            parsed_content = parser.parse(file_path)
            
            # Update doc metadata
            doc.page_count = parsed_content.page_count
            self.db.commit()
            
            # 3. Create Chunks
            splitter = SemanticTextSplitter(
                self.chunk_config.get_config(doc.file_type)
            )
            
            chunks = splitter.split_by_pages(
                parsed_content.page_texts,
                parsed_content.bounding_boxes,
                source_document=doc.filename
            )
            
            if not chunks:
                logger.warning(f"No text extracted from {doc.filename}")
                self.document_service.update_status(document_id, DocumentStatus.ERROR, "No text extracted")
                return

            # 4. Save Chunks to DB
            chunk_ids = []
            chunk_texts = []
            
            from dataclasses import asdict, is_dataclass
            
            for chunk in chunks:
                bbox = chunk.metadata.bounding_box
                # Convert BoundingBox dataclass to dict for JSON serialization
                if bbox and is_dataclass(bbox):
                    bbox = asdict(bbox)
                    
                db_chunk = ChunkModel(
                    document_id=document_id,
                    text=chunk.text,
                    chunk_index=chunk.metadata.chunk_index,
                    page_number=chunk.metadata.page_number,
                    bounding_box=bbox
                )
                self.db.add(db_chunk)
                # Flush to get ID
                self.db.flush()
                
                chunk_ids.append(db_chunk.id)
                chunk_texts.append(chunk.text)
                
            doc.chunk_count = len(chunks)
            self.db.commit()
            
            # 5. Index Chunks (Embeddings + FAISS)
            self.index_manager.add_document(document_id, chunk_texts, chunk_ids)
            
            # 6. Update Status to READY
            self.document_service.update_status(document_id, DocumentStatus.READY)
            logger.info(f"Successfully ingested document {doc.filename}")
            
        except Exception as e:
            logger.error(f"Ingestion failed for {document_id}: {e}")
            traceback.print_exc()
            self.db.rollback()  # Ensure transaction is rolled back before status update
            self.document_service.update_status(document_id, DocumentStatus.ERROR, str(e))
            raise
