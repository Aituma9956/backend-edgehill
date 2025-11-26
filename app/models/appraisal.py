from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum
from app.models.student import Student

class AppraisalStatus(enum.Enum):
    PENDING = "pending"
    STUDENT_SUBMITTED = "student_submitted"
    DOS_SUBMITTED = "dos_submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    UNSATISFACTORY = "unsatisfactory"
    RESUBMISSION_REQUIRED = "resubmission_required"

class Appraisal(Base):
    __tablename__ = "appraisals"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    academic_year = Column(String(10), nullable=False)
    appraisal_period = Column(String(50))
    due_date = Column(Date)
    student_submission_date = Column(DateTime(timezone=True))
    dos_submission_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    student_progress_report = Column(Text)
    student_achievements = Column(Text)
    student_challenges = Column(Text)
    student_goals = Column(Text)
    student_development_needs = Column(Text)
    dos_comments = Column(Text)
    dos_progress_rating = Column(String(20))  # excellent, good, satisfactory, unsatisfactory
    dos_recommendations = Column(Text)
    status = Column(Enum(AppraisalStatus), default=AppraisalStatus.PENDING)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewer_comments = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"))
    action_required = Column(Boolean, default=False)
    action_description = Column(Text)
    action_deadline = Column(Date)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student = relationship("Student", back_populates="appraisals")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Appraisal(student='{self.student_number}', year='{self.academic_year}', status='{self.status}')>"

Student.appraisals = relationship("Appraisal", back_populates="student")
