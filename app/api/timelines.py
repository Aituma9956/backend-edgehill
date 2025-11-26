from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.schemas.timeline import TimelineCreate, TimelineUpdate, Timeline
from app.services.timeline_service import TimelineService
from datetime import date

router = APIRouter()

@router.post("/", response_model=Timeline)
def create_timeline(
    timeline: TimelineCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return TimelineService.create_timeline(db, timeline)

@router.get("/student/{student_number}", response_model=List[Timeline])
def get_student_timeline(
    student_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return TimelineService.get_student_timelines(db, student_number, current_user)

@router.get("/", response_model=List[Timeline])
def get_timelines(
    skip: int = 0,
    limit: int = 100,
    student_number: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return TimelineService.get_timelines(db, current_user, skip, limit, student_number, stage, status)

@router.get("/{timeline_id}", response_model=Timeline)
def get_timeline(
    timeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return TimelineService.get_timeline_by_id(db, timeline_id, current_user)

@router.put("/{timeline_id}", response_model=Timeline)
def update_timeline(
    timeline_id: int,
    timeline_update: TimelineUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return TimelineService.update_timeline(db, timeline_id, timeline_update)

@router.put("/{timeline_id}/complete", response_model=Timeline)
def complete_timeline_milestone(
    timeline_id: int,
    actual_date: date,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin", "dos", "student"]))
):
    return TimelineService.complete_milestone(db, timeline_id, actual_date, current_user, notes)

@router.delete("/{timeline_id}")
def delete_timeline(
    timeline_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    TimelineService.delete_timeline(db, timeline_id)
    return {"message": "Timeline milestone deleted successfully"}
