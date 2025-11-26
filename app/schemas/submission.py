from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class SubmissionTypeEnum(str, Enum):
    REGISTRATION = "registration"
    VIVA_DOCUMENT = "viva_document"
    THESIS = "thesis"
    CORRECTION = "correction"
    ANNUAL_REPORT = "annual_report"

class SubmissionStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"

class SubmissionBase(BaseModel):
    student_number: str
    submission_type: SubmissionTypeEnum
    title: str
    description: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SubmissionStatusEnum] = None
    review_deadline: Optional[date] = None
    review_comments: Optional[str] = None

class SubmissionInDB(SubmissionBase):
    id: int
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    status: SubmissionStatusEnum = SubmissionStatusEnum.DRAFT
    submission_date: Optional[datetime] = None
    review_deadline: Optional[date] = None
    reviewed_by: Optional[int] = None
    review_date: Optional[datetime] = None
    review_comments: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class Submission(SubmissionInDB):
    pass
