from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum
from app.models.student import Student

class SubmissionType(enum.Enum):
    REGISTRATION = "registration"
    VIVA_DOCUMENT = "viva_document"
    THESIS = "thesis"
    CORRECTION = "correction"
    ANNUAL_REPORT = "annual_report"

class SubmissionStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    submission_type = Column(Enum(SubmissionType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    file_name = Column(String(200))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.DRAFT)
    submission_date = Column(DateTime(timezone=True))
    review_deadline = Column(Date)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    review_date = Column(DateTime(timezone=True))
    review_comments = Column(Text)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    student = relationship("Student", back_populates="submissions")
    reviewer = relationship("User")
    
    def __repr__(self):
        return f"<Submission(student='{self.student_number}', type='{self.submission_type}', title='{self.title}')>"

Student.submissions = relationship("Submission", back_populates="student")
