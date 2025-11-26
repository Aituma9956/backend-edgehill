from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.models.appraisal import Appraisal, AppraisalStatus
from app.models.user import User
from app.schemas.appraisal import AppraisalCreate, AppraisalUpdate, Appraisal as AppraisalSchema

class AppraisalService:
    @staticmethod
    def get_appraisals(db: Session, skip: int = 0, limit: int = 100) -> List[Appraisal]:
        """Get list of appraisals with pagination"""
        return db.query(Appraisal).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_appraisal_by_id(db: Session, appraisal_id: int) -> Optional[Appraisal]:
        """Get appraisal by ID"""
        return db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
    
    @staticmethod
    def get_appraisals_by_student(db: Session, student_number: str) -> List[Appraisal]:
        """Get appraisals by student number"""
        return db.query(Appraisal).filter(Appraisal.student_number == student_number).all()
    
    @staticmethod
    def create_appraisal(db: Session, appraisal_data: AppraisalCreate) -> AppraisalSchema:
        """Create a new appraisal"""
        appraisal = Appraisal(**appraisal_data.dict())
        db.add(appraisal)
        db.commit()
        db.refresh(appraisal)
        return AppraisalSchema.from_orm(appraisal)
    
    @staticmethod
    def get_student_appraisals(db: Session, student_number: str, current_user: User) -> List[AppraisalSchema]:
        """Get appraisals for a specific student with authorization check"""
        if current_user.role == "student" and student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view these appraisals")
        
        appraisals = db.query(Appraisal).filter(Appraisal.student_number == student_number).all()
        return [AppraisalSchema.from_orm(appraisal) for appraisal in appraisals]
    
    @staticmethod
    def submit_student_appraisal(db: Session, appraisal_id: int, appraisal_update: AppraisalUpdate, current_user: User) -> AppraisalSchema:
        """Submit student part of appraisal"""
        appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")

        if current_user.role == "student" and appraisal.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to submit this appraisal")

        # Only allow updating student-specific fields
        student_fields = ["student_progress_report", "student_achievements", "student_challenges", 
                         "student_goals", "student_development_needs"]
        update_data = appraisal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in student_fields:
                setattr(appraisal, field, value)
        
        appraisal.student_submission_date = datetime.now()
        appraisal.status = AppraisalStatus.STUDENT_SUBMITTED
        
        db.commit()
        db.refresh(appraisal)
        return AppraisalSchema.from_orm(appraisal)
    
    @staticmethod
    def submit_dos_appraisal(db: Session, appraisal_id: int, appraisal_update: AppraisalUpdate) -> AppraisalSchema:
        """Submit DOS part of appraisal"""
        appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")

        # Only allow updating DOS-specific fields
        dos_fields = ["dos_comments", "dos_progress_rating", "dos_recommendations"]
        update_data = appraisal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in dos_fields:
                setattr(appraisal, field, value)
        
        appraisal.dos_submission_date = datetime.now()
        appraisal.status = AppraisalStatus.DOS_SUBMITTED
        
        db.commit()
        db.refresh(appraisal)
        return AppraisalSchema.from_orm(appraisal)
    
    @staticmethod
    def approve_appraisal(db: Session, appraisal_id: int, current_user: User) -> AppraisalSchema:
        """Approve an appraisal - only admins can approve"""
        if current_user.role not in ["system_admin", "gbos_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to approve appraisals")
        
        appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")

        appraisal.status = AppraisalStatus.APPROVED
        appraisal.approved_date = datetime.now()
        appraisal.approved_by = current_user.username
        
        db.commit()
        db.refresh(appraisal)
        return AppraisalSchema.from_orm(appraisal)
    
    @staticmethod
    def review_appraisal(db: Session, appraisal_id: int, review_data: dict, current_user: User) -> AppraisalSchema:
        """Review an appraisal - can approve or mark as unsatisfactory"""
        if current_user.role not in ["system_admin", "gbos_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to review appraisals")
        
        appraisal = db.query(Appraisal).filter(Appraisal.id == appraisal_id).first()
        if not appraisal:
            raise HTTPException(status_code=404, detail="Appraisal not found")
        
        status = review_data.get("status")
        review_comments = review_data.get("review_comments")
        
        if status == "approved":
            appraisal.status = AppraisalStatus.APPROVED
            appraisal.approved_date = datetime.now()
            appraisal.approved_by = current_user.username
        elif status == "unsatisfactory":
            appraisal.status = AppraisalStatus.UNSATISFACTORY
            appraisal.review_date = datetime.now()
            appraisal.reviewed_by = current_user.username
        
        if review_comments:
            appraisal.admin_comments = review_comments
        
        db.commit()
        db.refresh(appraisal)
        return AppraisalSchema.from_orm(appraisal)

    # Legacy methods for backward compatibility - can be removed if not used elsewhere
    @staticmethod
    def get_appraisals_by_status(db: Session, status: str) -> List[Appraisal]:
        """Get appraisals by status"""
        return db.query(Appraisal).filter(Appraisal.status == status).all()
    
    @staticmethod
    def get_pending_appraisals(db: Session) -> List[Appraisal]:
        """Get all pending appraisals"""
        return db.query(Appraisal).filter(
            Appraisal.status.in_(["submitted", "in_progress"])
        ).all()
