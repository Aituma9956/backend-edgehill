from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.services.supervisor_service import SupervisorService
from app.schemas.supervisor import SupervisorCreate, SupervisorUpdate, Supervisor

router = APIRouter()

@router.post("/", response_model=Supervisor)
def create_supervisor(
    supervisor: SupervisorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    return SupervisorService.create_supervisor(db, supervisor)

@router.get("/", response_model=List[Supervisor])
def get_supervisors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    if search:
        return SupervisorService.search_supervisors(db, search)
    
    if department:
        return SupervisorService.get_supervisors_by_department(db, department)
    
    return SupervisorService.get_supervisors(db, skip, limit)

@router.get("/{supervisor_id}", response_model=Supervisor)
def get_supervisor(
    supervisor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    return SupervisorService.get_supervisor_by_id(db, supervisor_id)

@router.put("/{supervisor_id}", response_model=Supervisor)
def update_supervisor(
    supervisor_id: int,
    supervisor_update: SupervisorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    return SupervisorService.update_supervisor(db, supervisor_id, supervisor_update)

@router.delete("/{supervisor_id}")
def delete_supervisor(
    supervisor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin"]))
):
    SupervisorService.delete_supervisor(db, supervisor_id)
    return {"message": "Supervisor deleted successfully"}
