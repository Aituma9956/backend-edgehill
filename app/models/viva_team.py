from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum
from app.models.student import Student

class VivaStage(enum.Enum):
    REGISTRATION = "registration"
    PROGRESSION = "progression"
    FINAL = "final"

class VivaStatus(enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"

class VivaTeam(Base):
    __tablename__ = "viva_teams"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    stage = Column(Enum(VivaStage), nullable=False)
    status = Column(Enum(VivaStatus), default=VivaStatus.PROPOSED)
    internal_examiner_1_id = Column(Integer, ForeignKey("supervisors.supervisor_id"))
    internal_examiner_2_id = Column(Integer, ForeignKey("supervisors.supervisor_id"))
    external_examiner_name = Column(String(150))
    external_examiner_email = Column(String(100))
    external_examiner_institution = Column(String(200))
    proposed_date = Column(Date)
    scheduled_date = Column(Date)
    actual_date = Column(Date)
    location = Column(String(200))
    outcome = Column(String(50))  # pass, pass_with_minor_corrections, pass_with_major_corrections, fail, etc.
    outcome_notes = Column(Text)
    proposed_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student = relationship("Student", back_populates="viva_teams")
    internal_examiner_1 = relationship("Supervisor", foreign_keys=[internal_examiner_1_id])
    internal_examiner_2 = relationship("Supervisor", foreign_keys=[internal_examiner_2_id])
    proposer = relationship("User", foreign_keys=[proposed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<VivaTeam(student='{self.student_number}', stage='{self.stage}', status='{self.status}')>"

Student.viva_teams = relationship("VivaTeam", back_populates="student")
