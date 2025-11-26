from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    student_number: str
    forename: str
    surname: str
    cohort: Optional[str] = None
    course_code: Optional[str] = None
    quercus_course_name: Optional[str] = None
    subject_area: Optional[str] = None
    programme_of_study: Optional[str] = None
    mode: Optional[str] = None
    international_student: bool = False
    previous_ehu_student: bool = False
    previous_ehu_undergraduate: bool = False
    previous_ehu_pgt_student: bool = False
    previous_ehu_mres_student: bool = False
    previous_institution: Optional[str] = None
    student_notes: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    forename: Optional[str] = None
    surname: Optional[str] = None
    cohort: Optional[str] = None
    course_code: Optional[str] = None
    quercus_course_name: Optional[str] = None
    subject_area: Optional[str] = None
    programme_of_study: Optional[str] = None
    mode: Optional[str] = None
    international_student: Optional[bool] = None
    previous_ehu_student: Optional[bool] = None
    previous_ehu_undergraduate: Optional[bool] = None
    previous_ehu_pgt_student: Optional[bool] = None
    previous_ehu_mres_student: Optional[bool] = None
    previous_institution: Optional[str] = None
    student_notes: Optional[str] = None

class StudentInDB(StudentBase):
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class Student(StudentInDB):
    pass
