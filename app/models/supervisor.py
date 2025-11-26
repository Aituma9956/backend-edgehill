from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base

class Supervisor(Base):
    __tablename__ = "supervisors"
    supervisor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supervisor_name = Column(String(150), nullable=False)
    email = Column(String(100))
    department = Column(String(100))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    supervisor_notes = Column(Text, comment="Notes about supervisor specializations - availability or supervisory preferences")
    
    def __repr__(self):
        return f"<Supervisor(id={self.supervisor_id}, name='{self.supervisor_name}', department='{self.department}')>"
