from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pathlib import Path
import shutil
import os

from src.storage.db.database import get_db
from src.utils.config import get_settings
from src.workers.tasks import parse_questionnaire_async
from src.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
)
from src.storage.db.models import ProjectModel

router = APIRouter(tags=["projects"])


@router.post("/create-project", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
) -> Project:
    """Create a new project."""
    # Stub implementation
    db_project = ProjectModel(
        name=project.name,
        description=project.description,
        scope_type=project.scope_type,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return Project.model_validate(db_project)


@router.get("/list-projects", response_model=List[Project])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Project]:
    """List all projects."""
    # Stub implementation
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return [Project.model_validate(p) for p in projects]


@router.get("/get-project-info", response_model=ProjectDetail)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> ProjectDetail:
    """Get project details."""
    # Stub implementation
    project = db.query(ProjectModel).filter(ProjectModel.id == str(project_id)).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    return ProjectDetail(
        id=UUID(project.id),
        name=project.name,
        description=project.description,
        scope_type=project.scope_type,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        sections=[],
        questions=[],
        document_count=len(project.documents) if project.documents else 0
    )


@router.put("/update-project", response_model=Project)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
) -> Project:
    """Update a project."""
    # Stub implementation
    db_project = db.query(ProjectModel).filter(ProjectModel.id == str(project_id)).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "document_ids":  # Handle document_ids separately
            setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    return Project.model_validate(db_project)


@router.delete("/delete-project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """Delete a project."""
    # Stub implementation
    db_project = db.query(ProjectModel).filter(ProjectModel.id == str(project_id)).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    db.delete(db_project)
    db.commit()


@router.post("/{project_id}/questionnaire", status_code=status.HTTP_202_ACCEPTED)
async def upload_questionnaire(
    project_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a questionnaire file and trigger async parsing.
    """
    settings = get_settings()
    
    # Verify project exists
    project = db.query(ProjectModel).filter(ProjectModel.id == str(project_id)).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
        
    # Validation
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf and .docx files are supported for questionnaires"
        )
        
    # Save file
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"questionnaire_{project_id}{file_ext}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
        
    # Trigger Celery task
    task = parse_questionnaire_async.delay(str(file_path), str(project_id))
    
    return {
        "request_id": task.id,
        "project_id": str(project_id),
        "status": "queued",
        "message": "Questionnaire uploaded and parsing started"
    }


@router.get("/get-project-status")
def get_project_status(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Get project status."""
    # Stub implementation
    db_project = db.query(ProjectModel).filter(ProjectModel.id == str(project_id)).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    return {
        "project_id": str(db_project.id),
        "status": db_project.status,
        "updated_at": db_project.updated_at.isoformat()
    }
