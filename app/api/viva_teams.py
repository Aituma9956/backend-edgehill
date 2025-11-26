from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.schemas.viva_team import VivaTeamCreate, VivaTeamUpdate, VivaTeam
from app.services.viva_team_service import VivaTeamService
from datetime import date

router = APIRouter()

@router.post("/", response_model=VivaTeam)
def propose_viva_team(
    viva_team: VivaTeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return VivaTeamService.propose_viva_team(db, viva_team, current_user)

@router.get("/", response_model=List[VivaTeam])
def get_viva_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_number: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VivaTeamService.get_viva_teams(db, current_user, skip, limit, student_number, stage, status)

@router.get("/{viva_team_id}", response_model=VivaTeam)
def get_viva_team(
    viva_team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VivaTeamService.get_viva_team_by_id(db, viva_team_id, current_user)

@router.put("/{viva_team_id}", response_model=VivaTeam)
def update_viva_team(
    viva_team_id: int,
    viva_team_update: VivaTeamUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return VivaTeamService.update_viva_team(db, viva_team_id, viva_team_update)

@router.post("/{viva_team_id}/approve")
def approve_viva_team(
    viva_team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    VivaTeamService.approve_viva_team(db, viva_team_id, current_user)
    return {"message": "Viva team approved successfully"}

@router.post("/{viva_team_id}/reject")
def reject_viva_team(
    viva_team_id: int,
    reason: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    VivaTeamService.reject_viva_team(db, viva_team_id, reason)
    return {"message": "Viva team rejected"}

@router.post("/{viva_team_id}/schedule")
def schedule_viva(
    viva_team_id: int,
    scheduled_date: date,
    location: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    VivaTeamService.schedule_viva(db, viva_team_id, scheduled_date, location)
    return {"message": "Viva scheduled successfully"}

@router.post("/{viva_team_id}/outcome")
def submit_viva_outcome(
    viva_team_id: int,
    outcome: str,
    outcome_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["gbos_approver"]))
):
    VivaTeamService.submit_viva_outcome(db, viva_team_id, outcome, outcome_notes)
    return {"message": "Viva outcome submitted successfully"}
