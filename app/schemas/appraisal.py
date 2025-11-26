from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class AppraisalStatusEnum(str, Enum):
    PENDING = "pending"
    STUDENT_SUBMITTED = "student_submitted"
    DOS_SUBMITTED = "dos_submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    UNSATISFACTORY = "unsatisfactory"
    RESUBMISSION_REQUIRED = "resubmission_required"

class AppraisalBase(BaseModel):
    student_number: str
    academic_year: str
    appraisal_period: Optional[str] = None
    due_date: Optional[date] = None

class AppraisalCreate(AppraisalBase):
    pass

class AppraisalStudentSubmission(BaseModel):
    student_progress_report: Optional[str] = None
    student_achievements: Optional[str] = None
    student_challenges: Optional[str] = None
    student_goals: Optional[str] = None
    student_development_needs: Optional[str] = None

class AppraisalDosSubmission(BaseModel):
    dos_comments: Optional[str] = None
    dos_progress_rating: Optional[str] = None
    dos_recommendations: Optional[str] = None

class AppraisalUpdate(BaseModel):
    appraisal_period: Optional[str] = None
    due_date: Optional[date] = None
    student_progress_report: Optional[str] = None
    student_achievements: Optional[str] = None
    student_challenges: Optional[str] = None
    student_goals: Optional[str] = None
    student_development_needs: Optional[str] = None
    dos_comments: Optional[str] = None
    dos_progress_rating: Optional[str] = None
    dos_recommendations: Optional[str] = None
    status: Optional[AppraisalStatusEnum] = None
    reviewer_comments: Optional[str] = None
    action_required: Optional[bool] = None
    action_description: Optional[str] = None
    action_deadline: Optional[date] = None

class AppraisalInDB(AppraisalBase):
    id: int
    status: AppraisalStatusEnum
    student_submission_date: Optional[datetime] = None
    dos_submission_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    student_progress_report: Optional[str] = None
    student_achievements: Optional[str] = None
    student_challenges: Optional[str] = None
    student_goals: Optional[str] = None
    student_development_needs: Optional[str] = None
    dos_comments: Optional[str] = None
    dos_progress_rating: Optional[str] = None
    dos_recommendations: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewer_comments: Optional[str] = None
    approved_by: Optional[int] = None
    action_required: bool = False
    action_description: Optional[str] = None
    action_deadline: Optional[date] = None
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class Appraisal(AppraisalInDB):
    pass
