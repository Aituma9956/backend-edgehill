from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.schemas.appraisal import AppraisalCreate, AppraisalUpdate, Appraisal
from app.services.appraisal_service import AppraisalService

router = APIRouter()

@router.post("/", response_model=Appraisal)
def create_appraisal(
    appraisal: AppraisalCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return AppraisalService.create_appraisal(db, appraisal)

@router.get("/student/{student_number}", response_model=List[Appraisal])
def get_student_appraisals(
    student_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return AppraisalService.get_student_appraisals(db, student_number, current_user)

@router.put("/{appraisal_id}/student-submission", response_model=Appraisal)
def submit_student_appraisal(
    appraisal_id: int,
    appraisal_update: AppraisalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return AppraisalService.submit_student_appraisal(db, appraisal_id, appraisal_update, current_user)

@router.put("/{appraisal_id}/dos-submission", response_model=Appraisal)
def submit_dos_appraisal(
    appraisal_id: int,
    appraisal_update: AppraisalUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
):
    return AppraisalService.submit_dos_appraisal(db, appraisal_id, appraisal_update)

@router.post("/{appraisal_id}/approve")
def approve_appraisal(
    appraisal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    AppraisalService.approve_appraisal(db, appraisal_id, current_user)
    return {"message": "Appraisal approved successfully"}

@router.put("/{appraisal_id}/review", response_model=Appraisal)
def review_appraisal(
    appraisal_id: int,
    review_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    return AppraisalService.review_appraisal(db, appraisal_id, review_data, current_user)
