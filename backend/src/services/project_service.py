"""
Project Service for managing project lifecycle and questionnaire parsing.
"""
import logging
from typing import Optional, List
from uuid import UUID
from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.project import ProjectCreate, ProjectUpdate, ProjectStatus
from src.storage.db.models import ProjectModel
from src.services.questionnaire.parser import QuestionnaireParser
from src.services.questionnaire.converter import QuestionnaireConverter
from src.services.document_service import DocumentService

logger = logging.getLogger(__name__)

class ProjectService:
    """
    Service for managing Question Projects.
    """

    def __init__(self, db: Session):
        self.db = db
        self.parser = QuestionnaireParser()
        self.converter = QuestionnaireConverter(db)
        self.doc_service = DocumentService(db)

    def create_project(self, project_in: ProjectCreate) -> ProjectModel:
        """
        Create a new project. 
        """
        project = ProjectModel(
            name=project_in.name,
            description=project_in.description,
            scope_type=project_in.scope_type,
            status=ProjectStatus.DRAFT
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project

    def get_project(self, project_id: UUID) -> Optional[ProjectModel]:
        """Get project by ID."""
        return self.db.query(ProjectModel).get(str(project_id))

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """List all projects."""
        return self.db.query(ProjectModel).offset(skip).limit(limit).all()

    def update_project(self, project_id: UUID, project_in: ProjectUpdate) -> Optional[ProjectModel]:
        """Update a project."""
        project = self.get_project(project_id)
        if not project:
            return None
            
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        project.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(project)
        return project

    def process_questionnaire_file(self, project_id: UUID, file_path: Path) -> ProjectModel:
        """
        Process a questionnaire file: Parse -> Convert -> Save Structure.
        This is typically called efficiently from a background task.
        """
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        try:
            logger.info(f"Processing questionnaire for project {project_id} from {file_path}")
            
            # 1. Update status
            project.status = ProjectStatus.PROCESSING
            self.db.commit()

            # 2. Parse file using Gemini
            parsed_data = self.parser.parse_file(file_path)
            
            # 3. Convert and save to DB
            self.converter.convert_and_save(project_id, parsed_data)
            
            # 4. Update status to READY (or REVIEW if that's the flow)
            # For now, READY means structure is ready for answer generation
            project.status = ProjectStatus.READY
            project.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Project {project_id} structure successfully created.")
            return project

        except Exception as e:
            logger.error(f"Failed to process questionnaire for project {project_id}: {e}")
            project.status = ProjectStatus.DRAFT # Revert to DRAFT on error? Or ERROR status?
            # We don't have an ERROR status in the Enum yet, maybe fallback to DRAFT or stay in PROCESSING
            # Let's revert to DRAFT so user can try again.
            self.db.commit()
            raise

