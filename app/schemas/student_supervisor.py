from pydantic import BaseModel
from typing import Optional
from datetime import date

class StudentSupervisorBase(BaseModel):
    student_number: str
    supervisor_id: int
    role: str
    start_date: Optional[date] = None
    supervision_notes: Optional[str] = None

class StudentSupervisorCreate(StudentSupervisorBase):
    pass

class StudentSupervisorUpdate(BaseModel):
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    supervision_notes: Optional[str] = None

class StudentSupervisorInDB(StudentSupervisorBase):
    student_supervisor_id: int
    end_date: Optional[date] = None
    
    class Config:
        from_attributes = True

class StudentSupervisor(StudentSupervisorInDB):
    pass
