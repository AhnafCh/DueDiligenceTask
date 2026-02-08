"""
Celery tasks for async processing.

This module will be fully implemented in Phase 2 (Document Ingestion)
and Phase 3 (Questionnaire Parsing).
"""

from src.workers.celery_app import celery_app


@celery_app.task(name="tasks.index_document")
def index_document_async(document_id: str):
    """
    Background task for document indexing.
    """
    # Stub implementation
    return {
        "document_id": document_id,
        "status": "pending",
        "message": "Document indexing not yet implemented (Phase 2)"
    }


@celery_app.task(name="tasks.generate_answers")
def generate_answers_async(project_id: str):
    """
    Background task for answer generation.
    """
    # Stub implementation
    return {
        "project_id": project_id,
        "status": "pending",
        "message": "Answer generation not yet implemented (Phase 4)"
    }


@celery_app.task(name="tasks.parse_questionnaire")
def parse_questionnaire_async(file_path: str, project_id: str):
    """
    Background task for questionnaire parsing.
    """
    # Stub implementation
    return {
        "project_id": project_id,
        "status": "pending",
        "message": "Questionnaire parsing not yet implemented (Phase 3)"
    }
