from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupervisorBase(BaseModel):
    supervisor_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    supervisor_notes: Optional[str] = None

class SupervisorCreate(SupervisorBase):
    pass

class SupervisorUpdate(BaseModel):
    supervisor_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    supervisor_notes: Optional[str] = None

class SupervisorInDB(SupervisorBase):
    supervisor_id: int
    created_date: datetime
    
    class Config:
        from_attributes = True

class Supervisor(SupervisorInDB):
    pass
