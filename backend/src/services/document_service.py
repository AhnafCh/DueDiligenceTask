"""Document Service for managing document lifecycle and database operations."""
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import UploadFile

from sqlalchemy.orm import Session
from src.models.document import Document, DocumentStatus, DocumentCreate

from src.utils.config import get_settings


logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_document(self, file: UploadFile) -> Document:
        """
        Save uploaded file and create document record.
        
        Args:
            file: Uploaded file
            
        Returns:
            Created Document object
            
        Raises:
            ValueError: If file type invalid or size too large
        """
        # Validate extension
        ext = Path(file.filename).suffix.lower()
        if ext not in self.settings.allowed_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
            
        # Create file path
        # Use timestamp to avoid collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = self.upload_dir / safe_filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {e}")
            raise IOError(f"Failed to save file: {e}")
            
        # Validate size
        file_size = file_path.stat().st_size
        if file_size > self.settings.max_file_size:
            file_path.unlink()  # Delete file
            raise ValueError(f"File too large: {file_size} bytes (max {self.settings.max_file_size})")
            
        # Create database record
        doc_create = DocumentCreate(
            filename=file.filename,
            file_type=ext,
            file_size=file_size,
            file_path=str(file_path)
        )
        
        # Map Pydantic to SQLAlchemy model (assuming mapped in db/models.py or using Pydantic model directly if using SQLModel)
        # Verify src/storage/db/models.py DocumentModel
        from src.storage.db.models import DocumentModel
        
        db_doc = DocumentModel(
            filename=doc_create.filename,
            file_type=doc_create.file_type,
            file_path=doc_create.file_path,
            file_size=doc_create.file_size,
            status=DocumentStatus.UPLOADED,
            uploaded_at=datetime.utcnow()
        )
        
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        
        return db_doc

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID."""
        from src.storage.db.models import DocumentModel
        return self.db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    def list_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """List all documents."""
        from src.storage.db.models import DocumentModel
        return self.db.query(DocumentModel).offset(skip).limit(limit).all()

    def update_status(self, document_id: str, status: DocumentStatus, error_message: str = None):
        """Update document status."""
        from src.storage.db.models import DocumentModel
        doc = self.get_document(document_id)
        if doc:
            doc.status = status
            if error_message:
                doc.error_message = error_message
            if status == DocumentStatus.READY:
                doc.indexed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(doc)
        return doc
        
    def delete_document(self, document_id: str):
        """Delete document and file."""
        from src.storage.db.models import DocumentModel
        doc = self.get_document(document_id)
        if not doc:
            return
            
        # Delete file
        try:
            file_path = Path(doc.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file {doc.file_path}: {e}")
            
        # Delete DB record
        self.db.delete(doc)
        self.db.commit()
