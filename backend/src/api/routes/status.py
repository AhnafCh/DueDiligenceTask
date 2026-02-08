from fastapi import APIRouter, HTTPException, status
from uuid import UUID

router = APIRouter(prefix="/requests", tags=["status"])


@router.get("/{request_id}")
def get_request_status(request_id: UUID) -> dict:
    """Get async task status."""
    # Stub implementation - will be fully implemented with Celery in Phase 2
    return {
        "request_id": str(request_id),
        "status": "pending",
        "progress": 0,
        "message": "Task status tracking not yet implemented"
    }


@router.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Questionnaire Agent API",
        "version": "1.0.0"
    }
