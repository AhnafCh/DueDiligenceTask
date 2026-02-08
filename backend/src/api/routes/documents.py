from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from src.storage.db.database import get_db
from src.services.document_service import DocumentService
from src.models.document import Document
from src.workers.tasks import index_document_async

router = APIRouter(tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("/upload-document", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Document:
    """
    Upload a document.
    Does not trigger indexing automatically to allow for separate triggering only if needed,
    but typically the UI might chain these calls. 
    (Revised: Actually, Phase 2 plan implies separate endpoints: upload, then index. 
    But often it's convenient to do both or have one endpoint. 
    The plan lists `POST /index-document-async` which implies it takes a file or ID.
    Let's stick to the plan: `upload-document` uploads, `index-document-async` triggers.)
    """
    service = DocumentService(db)
    try:
        return service.upload_document(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/documents", response_model=List[Document])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Document]:
    """List all documents."""
    service = DocumentService(db)
    return service.list_documents(skip, limit)


@router.get("/documents/{document_id}", response_model=Document)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> Document:
    """Get document details."""
    service = DocumentService(db)
    document = service.get_document(str(document_id))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    return document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """Delete a document."""
    service = DocumentService(db)
    document = service.get_document(str(document_id))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    service.delete_document(str(document_id))


@router.post("/index-document-async", response_model=dict)
def trigger_index_document(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """
    Trigger async document indexing for an existing document.
    """
    service = DocumentService(db)
    document = service.get_document(str(document_id))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    
    # Trigger Celery task
    task = index_document_async.delay(str(document_id))
    
    return {
        "request_id": task.id,
        "document_id": str(document_id),
        "status": "queued",
        "message": "Document indexing started in background"
    }


@router.get("/get-document-status", response_model=dict)
def get_document_status(
    document_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get document status."""
    service = DocumentService(db)
    document = service.get_document(str(document_id))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
        
    return {
        "document_id": str(document.id),
        "status": document.status,
        "chunk_count": document.chunk_count,
        "indexed_at": document.indexed_at,
        "error_message": document.error_message
    }
