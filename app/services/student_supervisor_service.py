from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from app.models.student_supervisor import StudentSupervisor
from app.models.user import User
from app.schemas.student_supervisor import (
    StudentSupervisorCreate, 
    StudentSupervisorUpdate, 
    StudentSupervisor as StudentSupervisorSchema
)

class StudentSupervisorService:
    @staticmethod
    def assign_supervisor_to_student(
        db: Session, 
        assignment: StudentSupervisorCreate, 
        current_user: User
    ) -> StudentSupervisorSchema:
        """Assign a supervisor to a student"""
        # Only admin roles can assign supervisors
        if current_user.role not in ["system_admin", "academic_admin", "gbos_admin", "dos"]:
            raise HTTPException(status_code=403, detail="Not authorized to assign supervisors")
        
        # Check if assignment already exists
        existing = db.query(StudentSupervisor).filter(
            StudentSupervisor.student_number == assignment.student_number,
            StudentSupervisor.supervisor_id == assignment.supervisor_id,
            StudentSupervisor.role == assignment.role
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="This supervisor assignment already exists")
        
        db_assignment = StudentSupervisor(**assignment.dict())
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return StudentSupervisorSchema.from_orm(db_assignment)
    
    @staticmethod
    def get_student_supervisors(
        db: Session, 
        student_number: str, 
        current_user: User
    ) -> List[StudentSupervisorSchema]:
        """Get all supervisors for a student"""
        # Students can only view their own supervisors
        if current_user.role == "student" and current_user.username != student_number:
            raise HTTPException(status_code=403, detail="Not authorized to view this student's supervisors")
        
        supervisors = db.query(StudentSupervisor).filter(
            StudentSupervisor.student_number == student_number
        ).all()
        return [StudentSupervisorSchema.from_orm(supervisor) for supervisor in supervisors]
    
    @staticmethod
    def get_supervisor_students(
        db: Session, 
        supervisor_id: int, 
        current_user: User
    ) -> List[StudentSupervisorSchema]:
        """Get all students for a supervisor"""
        # Supervisors can only view their own students, admins can view all
        if current_user.role == "supervisor":
            # Check if current user is the supervisor being queried
            # This would need additional logic to match user to supervisor record
            pass
        elif current_user.role not in ["system_admin", "academic_admin", "gbos_admin", "dos"]:
            raise HTTPException(status_code=403, detail="Not authorized to view supervisor's students")
        
        students = db.query(StudentSupervisor).filter(
            StudentSupervisor.supervisor_id == supervisor_id
        ).all()
        return [StudentSupervisorSchema.from_orm(student) for student in students]
    
    @staticmethod
    def update_supervisor_assignment(
        db: Session, 
        assignment_id: int, 
        assignment_update: StudentSupervisorUpdate, 
        current_user: User
    ) -> StudentSupervisorSchema:
        """Update a supervisor assignment"""
        if current_user.role not in ["system_admin", "academic_admin", "gbos_admin", "dos"]:
            raise HTTPException(status_code=403, detail="Not authorized to update supervisor assignments")
        
        assignment = db.query(StudentSupervisor).filter(
            StudentSupervisor.student_supervisor_id == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Supervisor assignment not found")
        
        update_data = assignment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        db.commit()
        db.refresh(assignment)
        return StudentSupervisorSchema.from_orm(assignment)
    
    @staticmethod
    def remove_supervisor_assignment(
        db: Session, 
        assignment_id: int, 
        current_user: User
    ) -> bool:
        """Remove a supervisor assignment"""
        if current_user.role not in ["system_admin", "academic_admin", "gbos_admin", "dos"]:
            raise HTTPException(status_code=403, detail="Not authorized to remove supervisor assignments")
        
        assignment = db.query(StudentSupervisor).filter(
            StudentSupervisor.student_supervisor_id == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=404, detail="Supervisor assignment not found")
        
        db.delete(assignment)
        db.commit()
        return True
    
    @staticmethod
    def get_all_assignments(
        db: Session, 
        current_user: User, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[StudentSupervisorSchema]:
        """Get all supervisor assignments (admin only)"""
        if current_user.role not in ["system_admin", "academic_admin", "gbos_admin", "dos"]:
            raise HTTPException(status_code=403, detail="Not authorized to view all assignments")
        
        assignments = db.query(StudentSupervisor).offset(skip).limit(limit).all()
        return [StudentSupervisorSchema.from_orm(assignment) for assignment in assignments]
