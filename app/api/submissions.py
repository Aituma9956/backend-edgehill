from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.schemas.submission import SubmissionCreate, SubmissionUpdate, Submission
from app.services.submission_service import SubmissionService

router = APIRouter()

@router.post("/", response_model=Submission)
def create_submission(
    submission: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return SubmissionService.create_submission(db, submission, current_user)

@router.get("/", response_model=List[Submission])
def get_submissions(
    student_number: Optional[str] = None,
    submission_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return SubmissionService.get_submissions(db, current_user, student_number, submission_type, status)

@router.get("/{submission_id}", response_model=Submission)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return SubmissionService.get_submission_by_id(db, submission_id, current_user)

@router.post("/{submission_id}/upload")
async def upload_file(
    submission_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await SubmissionService.upload_file(db, submission_id, file, current_user)

@router.put("/{submission_id}", response_model=Submission)
def update_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return SubmissionService.update_submission(db, submission_id, submission_update, current_user)

@router.post("/{submission_id}/approve")
def approve_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin", "dos", "examiner"]))
):
    SubmissionService.approve_submission(db, submission_id, current_user)
    return {"message": "Submission approved successfully"}

@router.post("/{submission_id}/reject")
def reject_submission(
    submission_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin", "dos", "examiner"]))
):
    SubmissionService.reject_submission(db, submission_id, reason, current_user)
    return {"message": "Submission rejected"}

@router.put("/{submission_id}/review", response_model=Submission)
def review_submission(
    submission_id: int,
    review_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["system_admin", "gbos_admin", "dos", "examiner"]))
):
    return SubmissionService.review_submission(db, submission_id, review_data, current_user)
