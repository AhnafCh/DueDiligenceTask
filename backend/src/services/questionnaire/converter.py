"""
Converter for transforming parsed questionnaire models into database entities.
"""
import logging
from uuid import UUID
from sqlalchemy.orm import Session

from src.models.project import ProjectStatus
from src.services.questionnaire.models import ParsedQuestionnaire
from src.storage.db.models import ProjectModel, SectionModel, QuestionModel

logger = logging.getLogger(__name__)

class QuestionnaireConverter:
    """
    Converts parsed questionnaire data into database models.
    """

    def __init__(self, db: Session):
        self.db = db

    def convert_and_save(self, project_id: UUID, parsed_data: ParsedQuestionnaire) -> ProjectModel:
        """
        Converts parsed data into Section and Question entities for a given project.
        
        Args:
            project_id: The ID of the project to populate.
            parsed_data: The structured data extracted from the questionnaire.
            
        Returns:
            The updated Project entity.
        """
        project_id_str = str(project_id)
        project = self.db.query(ProjectModel).get(project_id_str)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        try:
            # Clear existing sections and questions if any (re-parsing scenario)
            # Note: In a real re-parsing scenario, we might want to be smarter about updates
            # to preserve existing answers, but for now we'll assume a fresh start or full replace.
            self._clear_existing_structure(project_id_str)

            for section_data in parsed_data.sections:
                # Create Section
                section = SectionModel(
                    project_id=project_id_str,
                    title=section_data.title,
                    order=section_data.order
                )
                self.db.add(section)
                self.db.flush() # Flush to get section.id

                for question_data in section_data.questions:
                    # Create Question
                    question = QuestionModel(
                        project_id=project_id_str,
                        section_id=section.id,
                        text=question_data.text,
                        order=question_data.order,
                        expected_answer_type=question_data.expected_answer_type
                    )
                    self.db.add(question)
            
            # Update project status
            project.status = ProjectStatus.PROCESSING
            self.db.commit()
            logger.info(f"Successfully converted and saved structure for project {project_id}")
            return project

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to convert/save project structure: {e}")
            raise

    def _clear_existing_structure(self, project_id: str):
        """Helper to remove existing sections/questions for a project."""
        self.db.query(QuestionModel).filter(QuestionModel.project_id == project_id).delete()
        self.db.query(SectionModel).filter(SectionModel.project_id == project_id).delete()
        self.db.flush()
