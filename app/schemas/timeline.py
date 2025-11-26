from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

class TimelineStageEnum(str, Enum):
    PROPOSAL = "proposal"
    PROGRESSION = "progression"
    FINAL = "final"

class TimelineBase(BaseModel):
    student_number: str
    stage: TimelineStageEnum
    milestone_name: str
    planned_date: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None

class TimelineCreate(TimelineBase):
    pass

class TimelineUpdate(BaseModel):
    stage: Optional[TimelineStageEnum] = None
    milestone_name: Optional[str] = None
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None

class TimelineInDB(TimelineBase):
    id: int
    actual_date: Optional[date] = None
    status: str = "pending"
    
    class Config:
        from_attributes = True

class Timeline(TimelineInDB):
    pass
