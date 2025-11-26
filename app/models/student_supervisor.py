from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.student import Student
from app.models.supervisor import Supervisor

class StudentSupervisor(Base):
    __tablename__ = "student_supervisors"
    student_supervisor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("supervisors.supervisor_id"), nullable=False)
    role = Column(String(50), nullable=False)  # Director of Studies, Supervisor 1, Supervisor 2, etc.
    start_date = Column(Date)
    end_date = Column(Date)
    supervision_notes = Column(Text, comment="Notes about the supervision arrangement - changes in roles or specific supervision requirements")
    student = relationship("Student", back_populates="supervisors")
    supervisor = relationship("Supervisor", back_populates="students")
    
    def __repr__(self):
        return f"<StudentSupervisor(student='{self.student_number}', supervisor={self.supervisor_id}, role='{self.role}')>"

Student.supervisors = relationship("StudentSupervisor", back_populates="student")
Supervisor.students = relationship("StudentSupervisor", back_populates="supervisor")
