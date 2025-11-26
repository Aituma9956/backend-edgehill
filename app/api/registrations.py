from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.schemas.registration import RegistrationCreate, RegistrationUpdate, Registration
from app.services.registration_service import RegistrationService

router = APIRouter()

@router.post("/", response_model=Registration)
def create_registration(
    registration: RegistrationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "academic_admin", "gbos_admin"]))
):
    return RegistrationService.create_registration(db, registration)

@router.get("/", response_model=List[Registration])
def get_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_number: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RegistrationService.get_registrations(db, current_user, skip, limit, student_number, status)

@router.get("/{registration_id}", response_model=Registration)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RegistrationService.get_registration_by_id(db, registration_id, current_user)

@router.get("/student/{student_number}", response_model=Registration)
def get_registration_by_student(
    student_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return RegistrationService.get_registration_by_student(db, student_number, current_user)

@router.put("/{registration_id}", response_model=Registration)
def update_registration(
    registration_id: int,
    registration_update: RegistrationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "academic_admin", "gbos_admin"]))
):
    return RegistrationService.update_registration(db, registration_id, registration_update)

@router.post("/{registration_id}/extension")
def request_extension(
    registration_id: int,
    extension_days: int,
    reason: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "academic_admin", "gbos_admin", "dos"]))
):
    RegistrationService.request_extension(db, registration_id, extension_days, reason)
    return {"message": "Extension request submitted successfully"}

@router.post("/{registration_id}/extension/approve")
def approve_extension(
    registration_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    RegistrationService.approve_extension(db, registration_id)
    return {"message": "Extension approved successfully"}
