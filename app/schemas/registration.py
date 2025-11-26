from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class RegistrationBase(BaseModel):
    student_number: str
    registration_status: Optional[str] = None
    original_registration_deadline: Optional[date] = None
    registration_extension_request_date: Optional[date] = None
    date_of_registration_extension_approval: Optional[date] = None
    registration_extension_length_days: Optional[int] = None
    revised_registration_deadline: Optional[date] = None
    date_pgr_moved_to_new_blackboard_group: Optional[date] = None
    pgr_registration_process_completed: bool = False

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(BaseModel):
    registration_status: Optional[str] = None
    original_registration_deadline: Optional[date] = None
    registration_extension_request_date: Optional[date] = None
    date_of_registration_extension_approval: Optional[date] = None
    registration_extension_length_days: Optional[int] = None
    revised_registration_deadline: Optional[date] = None
    date_pgr_moved_to_new_blackboard_group: Optional[date] = None
    pgr_registration_process_completed: Optional[bool] = None

class RegistrationInDB(RegistrationBase):
    registration_id: int
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class Registration(RegistrationInDB):
    pass
