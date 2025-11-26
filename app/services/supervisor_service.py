from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.supervisor import Supervisor
from app.models.registration import Registration
from app.schemas.supervisor import SupervisorCreate, SupervisorUpdate, Supervisor as SupervisorSchema

class SupervisorService:
    @staticmethod
    def get_supervisors(db: Session, skip: int = 0, limit: int = 100) -> List[SupervisorSchema]:
        """Get list of supervisors with pagination"""
        supervisors = db.query(Supervisor).offset(skip).limit(limit).all()
        return [SupervisorSchema.from_orm(supervisor) for supervisor in supervisors]
    
    @staticmethod
    def get_supervisor_by_id(db: Session, supervisor_id: int) -> Optional[SupervisorSchema]:
        """Get supervisor by ID"""
        supervisor = db.query(Supervisor).filter(Supervisor.supervisor_id == supervisor_id).first()
        return SupervisorSchema.from_orm(supervisor) if supervisor else None
    
    @staticmethod
    def get_supervisor_by_email(db: Session, email: str) -> Optional[SupervisorSchema]:
        """Get supervisor by email"""
        supervisor = db.query(Supervisor).filter(Supervisor.email == email).first()
        return SupervisorSchema.from_orm(supervisor) if supervisor else None
    
    @staticmethod
    def create_supervisor(db: Session, supervisor_data: SupervisorCreate) -> SupervisorSchema:
        """Create a new supervisor"""
        supervisor = Supervisor(**supervisor_data.dict())
        db.add(supervisor)
        db.commit()
        db.refresh(supervisor)
        return SupervisorSchema.from_orm(supervisor)
    
    @staticmethod
    def update_supervisor(db: Session, supervisor_id: int, supervisor_data: SupervisorUpdate) -> Optional[SupervisorSchema]:
        """Update supervisor information"""
        supervisor = db.query(Supervisor).filter(Supervisor.supervisor_id == supervisor_id).first()
        if not supervisor:
            return None
        
        update_data = supervisor_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(supervisor, key) and value is not None:
                setattr(supervisor, key, value)
        
        db.commit()
        db.refresh(supervisor)
        return SupervisorSchema.from_orm(supervisor)
    
    @staticmethod
    def delete_supervisor(db: Session, supervisor_id: int) -> bool:
        """Delete a supervisor"""
        supervisor = db.query(Supervisor).filter(Supervisor.supervisor_id == supervisor_id).first()
        if not supervisor:
            return False
        
        db.delete(supervisor)
        db.commit()
        return True
    
    @staticmethod
    def search_supervisors(db: Session, query: str) -> List[Supervisor]:
        """Search supervisors by name or email"""
        return db.query(Supervisor).filter(
            Supervisor.first_name.ilike(f"%{query}%") |
            Supervisor.last_name.ilike(f"%{query}%") |
            Supervisor.email.ilike(f"%{query}%")
        ).all()
    
    @staticmethod
    def get_supervisors_by_department(db: Session, department: str) -> List[Supervisor]:
        """Get supervisors by department"""
        return db.query(Supervisor).filter(Supervisor.department == department).all()
    
    @staticmethod
    def get_supervisor_workload(db: Session, supervisor_id: int) -> dict:
        """Get supervisor's current workload"""
        active_students = db.query(Registration).filter(
            Registration.primary_supervisor_id == supervisor_id,
            Registration.status == "active"
        ).count()
        
        total_students = db.query(Registration).filter(
            Registration.primary_supervisor_id == supervisor_id
        ).count()
        
        return {
            "active_students": active_students,
            "total_students": total_students
        }
    
    @staticmethod
    def get_available_supervisors(db: Session, max_students: int = 10) -> List[Supervisor]:
        """Get supervisors with capacity for more students"""
        supervisors = db.query(Supervisor).all()
        available = []
        
        for supervisor in supervisors:
            workload = SupervisorService.get_supervisor_workload(db, supervisor.supervisor_id)
            if workload["active_students"] < max_students:
                available.append(supervisor)
        
        return available
