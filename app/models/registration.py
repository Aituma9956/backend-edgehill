from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.student import Student

class Registration(Base):
    __tablename__ = "registrations"
    registration_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    registration_status = Column(String(50))
    original_registration_deadline = Column(Date)
    registration_extension_request_date = Column(Date)
    date_of_registration_extension_approval = Column(Date)
    registration_extension_length_days = Column(Integer)
    revised_registration_deadline = Column(Date)
    date_pgr_moved_to_new_blackboard_group = Column(Date)
    pgr_registration_process_completed = Column(Boolean, default=False)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student = relationship("Student", back_populates="registrations")
    
    def __repr__(self):
        return f"<Registration(id={self.registration_id}, student='{self.student_number}', status='{self.registration_status}')>"

Student.registrations = relationship("Registration", back_populates="student")
