from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base

class Student(Base):
    __tablename__ = "students"
    student_number = Column(String(20), primary_key=True, index=True)
    forename = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    cohort = Column(String(50))
    course_code = Column(String(20))
    quercus_course_name = Column(String(200))
    subject_area = Column(String(100))
    programme_of_study = Column(String(200))
    mode = Column(String(50))  # Full-time/Part-time
    international_student = Column(Boolean, default=False)
    previous_ehu_student = Column(Boolean, default=False)
    previous_ehu_undergraduate = Column(Boolean, default=False)
    previous_ehu_pgt_student = Column(Boolean, default=False)
    previous_ehu_mres_student = Column(Boolean, default=False)
    previous_institution = Column(String(200))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student_notes = Column(Text, comment="General notes about the student - special circumstances or important background information")
    
    def __repr__(self):
        return f"<Student(student_number='{self.student_number}', name='{self.forename} {self.surname}')>"
