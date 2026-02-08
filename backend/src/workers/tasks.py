"""
Celery tasks for async processing.
"""
import logging
import traceback
from uuid import UUID

from src.workers.celery_app import celery_app
from src.storage.db.database import get_db, SessionLocal
from src.services.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.index_document", bind=True)
def index_document_async(self, document_id: str):
    """
    Background task for document indexing.
    Runs the full ingestion pipeline (Parse -> Chunk -> Embed -> Index).
    """
    logger.info(f"Starting async indexing for document {document_id}")
    
    db = SessionLocal()
    try:
        pipeline = IngestionPipeline(db)
        pipeline.run(document_id)
        
        return {
            "document_id": document_id,
            "status": "completed",
            "message": "Document successfully indexed"
        }
    except Exception as e:
        logger.error(f"Error in index_document_async: {e}")
        traceback.print_exc()
        return {
            "document_id": document_id,
            "status": "failed",
            "message": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="tasks.generate_answers")
def generate_answers_async(project_id: str):
    """
    Background task for answer generation.
    """
    # Stub implementation - Phase 4
    return {
        "project_id": project_id,
        "status": "pending",
        "message": "Answer generation not yet implemented (Phase 4)"
    }


@celery_app.task(name="tasks.parse_questionnaire", bind=True)
def parse_questionnaire_async(self, file_path: str, project_id: str):
    """
    Background task for questionnaire parsing.
    """
    logger.info(f"Starting async parsing for project {project_id} from {file_path}")
    
    db = SessionLocal()
    try:
        from src.services.project_service import ProjectService
        from pathlib import Path
        
        service = ProjectService(db)
        service.process_questionnaire_file(UUID(project_id), Path(file_path))
        
        return {
            "project_id": project_id,
            "status": "completed",
            "message": "Questionnaire successfully parsed and structure created"
        }
    except Exception as e:
        logger.error(f"Error in parse_questionnaire_async: {e}")
        traceback.print_exc()
        return {
            "project_id": project_id,
            "status": "failed",
            "message": str(e)
        }
    finally:
        db.close()
