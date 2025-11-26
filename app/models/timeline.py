from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from app.models.student import Student

class TimelineStage(enum.Enum):
    PROPOSAL = "proposal"
    PROGRESSION = "progression"
    FINAL = "final"

class Timeline(Base):
    __tablename__ = "timelines"
    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(20), ForeignKey("students.student_number"), nullable=False)
    stage = Column(Enum(TimelineStage), nullable=False)
    milestone_name = Column(String(100), nullable=False)
    planned_date = Column(Date)
    actual_date = Column(Date)
    status = Column(String(50), default="pending")  # pending, completed, overdue
    description = Column(Text)
    notes = Column(Text)

    student = relationship("Student", back_populates="timelines")
    
    def __repr__(self):
        return f"<Timeline(student='{self.student_number}', stage='{self.stage}', milestone='{self.milestone_name}')>"

Student.timelines = relationship("Timeline", back_populates="student")
