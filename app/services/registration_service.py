from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from fastapi import HTTPException
from app.models.registration import Registration
from app.models.user import User
from app.schemas.registration import RegistrationCreate, RegistrationUpdate, Registration as RegistrationSchema

class RegistrationService:
    @staticmethod
    def create_registration(db: Session, registration: RegistrationCreate) -> RegistrationSchema:
        """Create a new registration"""
        db_registration = Registration(**registration.dict())
        db.add(db_registration)
        db.commit()
        db.refresh(db_registration)
        return RegistrationSchema.from_orm(db_registration)
    
    @staticmethod
    def get_registrations(db: Session, current_user: User, skip: int = 0, limit: int = 100,
                         student_number: Optional[str] = None, status: Optional[str] = None) -> List[RegistrationSchema]:
        """Get registrations with filtering and authorization"""
        query = db.query(Registration)

        if student_number:
            query = query.filter(Registration.student_number.ilike(f"%{student_number}%"))
        
        if status:
            query = query.filter(Registration.status == status)

        # Students can only see their own registrations
        if current_user.role == "student":
            query = query.filter(Registration.student_number == current_user.username)
        
        registrations = query.offset(skip).limit(limit).all()
        return [RegistrationSchema.from_orm(registration) for registration in registrations]
    
    @staticmethod
    def get_registration_by_id(db: Session, registration_id: int, current_user: User) -> RegistrationSchema:
        """Get registration by ID with authorization check"""
        registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")

        # Students can only view their own registrations
        if current_user.role == "student" and registration.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view this registration")
        
        return RegistrationSchema.from_orm(registration)
    
    @staticmethod
    def get_registration_by_student(db: Session, student_number: str, current_user: User) -> RegistrationSchema:
        """Get registration by student number with authorization check"""
        if current_user.role == "student" and current_user.username != student_number:
            raise HTTPException(status_code=403, detail="Not authorized to view this registration")
        
        registration = db.query(Registration).filter(Registration.student_number == student_number).first()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        return RegistrationSchema.from_orm(registration)
    
    @staticmethod
    def update_registration(db: Session, registration_id: int, registration_update: RegistrationUpdate) -> RegistrationSchema:
        """Update registration information"""
        db_registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
        if not db_registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        update_data = registration_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_registration, field, value)
        
        db.commit()
        db.refresh(db_registration)
        return RegistrationSchema.from_orm(db_registration)
    
    @staticmethod
    def request_extension(db: Session, registration_id: int, extension_days: int, reason: str) -> RegistrationSchema:
        """Request extension for registration"""
        registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        registration.extension_requested = True
        registration.extension_period = extension_days
        registration.extension_reason = reason
        db.commit()
        db.refresh(registration)
        return RegistrationSchema.from_orm(registration)
    
    @staticmethod
    def approve_extension(db: Session, registration_id: int) -> RegistrationSchema:
        """Approve extension for registration"""
        registration = db.query(Registration).filter(Registration.registration_id == registration_id).first()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        registration.extension_approved = True
        registration.extension_approved_date = datetime.now()
        # Add extension period to the due date
        if registration.extension_period and registration.due_date:
            from datetime import timedelta
            registration.due_date = registration.due_date + timedelta(days=registration.extension_period)
        
        db.commit()
        db.refresh(registration)
        return RegistrationSchema.from_orm(registration)
