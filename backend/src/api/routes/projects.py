from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from src.storage.db.database import get_db
from src.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectDetail,
)
from src.storage.db.models import ProjectModel

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
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


@router.get("/", response_model=List[Project])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[Project]:
    """List all projects."""
    # Stub implementation
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return [Project.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectDetail)
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


@router.put("/{project_id}", response_model=Project)
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


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/{project_id}/create-async")
def create_project_async(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Trigger async project creation."""
    # Stub implementation - will be implemented in Phase 3
    return {
        "request_id": str(UUID("00000000-0000-0000-0000-000000000000")),
        "status": "pending",
        "message": "Project creation queued (stub)"
    }


@router.post("/{project_id}/update-async")
def update_project_async(
    project_id: UUID,
    db: Session = Depends(get_db)
) -> dict:
    """Trigger async project update."""
    # Stub implementation - will be implemented in Phase 3
    return {
        "request_id": str(UUID("00000000-0000-0000-0000-000000000000")),
        "status": "pending",
        "message": "Project update queued (stub)"
    }


@router.get("/{project_id}/status")
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
