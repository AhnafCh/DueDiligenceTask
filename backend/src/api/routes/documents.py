from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import os
from pathlib import Path

from src.storage.db.database import get_db
from src.models.document import (
    Document,
    DocumentCreate,
    DocumentUpdate,
    DocumentStatus,
)
from src.storage.db.models import DocumentModel

router = APIRouter(prefix="/documents", tags=["documents"])

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Document:
    """Upload a document."""
    # Stub implementation
    file_path = UPLOAD_DIR / file.filename
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Get file info
    file_size = len(content)
    file_type = file.filename.split(".")[-1].lower()
    
    # Create database entry
    db_document = DocumentModel(
        filename=file.filename,
        file_type=file_type,
        file_path=str(file_path),
        file_size=file_size,
        status=DocumentStatus.UPLOADED
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return Document.model_validate(db_document)


@router.get("/", response_model=List[Document])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Document]:
    """List all documents."""
    # Stub implementation
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    return [Document.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> Document:
    """Get document details."""
    # Stub implementation
    document = db.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    return Document.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """Delete a document."""
    # Stub implementation
    db_document = db.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    # Delete file
    if os.path.exists(db_document.file_path):
        os.remove(db_document.file_path)
    
    db.delete(db_document)
    db.commit()


@router.post("/{document_id}/index-async")
def index_document_async(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Trigger async document indexing."""
    # Stub implementation - will be implemented in Phase 2
    db_document = db.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    return {
        "request_id": str(UUID("00000000-0000-0000-0000-000000000000")),
        "status": "pending",
        "message": "Document indexing queued (stub)"
    }


@router.get("/{document_id}/status")
def get_document_status(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get document indexing status."""
    # Stub implementation
    db_document = db.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    return {
        "document_id": str(db_document.id),
        "status": db_document.status,
        "chunk_count": db_document.chunk_count,
        "indexed_at": db_document.indexed_at.isoformat() if db_document.indexed_at else None
    }
