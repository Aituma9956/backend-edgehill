from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class VivaStageEnum(str, Enum):
    REGISTRATION = "registration"
    PROGRESSION = "progression"
    FINAL = "final"

class VivaStatusEnum(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"

class VivaTeamBase(BaseModel):
    student_number: str
    stage: VivaStageEnum
    internal_examiner_1_id: Optional[int] = None
    internal_examiner_2_id: Optional[int] = None
    external_examiner_name: Optional[str] = None
    external_examiner_email: Optional[str] = None
    external_examiner_institution: Optional[str] = None
    proposed_date: Optional[date] = None
    location: Optional[str] = None

class VivaTeamCreate(VivaTeamBase):
    pass

class VivaTeamUpdate(BaseModel):
    stage: Optional[VivaStageEnum] = None
    status: Optional[VivaStatusEnum] = None
    internal_examiner_1_id: Optional[int] = None
    internal_examiner_2_id: Optional[int] = None
    external_examiner_name: Optional[str] = None
    external_examiner_email: Optional[str] = None
    external_examiner_institution: Optional[str] = None
    proposed_date: Optional[date] = None
    scheduled_date: Optional[date] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    outcome_notes: Optional[str] = None

class VivaTeamInDB(VivaTeamBase):
    id: int
    status: VivaStatusEnum
    scheduled_date: Optional[date] = None
    actual_date: Optional[date] = None
    outcome: Optional[str] = None
    outcome_notes: Optional[str] = None
    proposed_by: Optional[int] = None
    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class VivaTeam(VivaTeamInDB):
    pass
