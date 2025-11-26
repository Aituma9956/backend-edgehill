from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.student_supervisor_service import StudentSupervisorService
from app.schemas.student_supervisor import (
    StudentSupervisorCreate,
    StudentSupervisorUpdate,
    StudentSupervisor as StudentSupervisorResponse
)

router = APIRouter()

@router.post("/assign", response_model=StudentSupervisorResponse)
def assign_supervisor_to_student(
    assignment: StudentSupervisorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign a supervisor to a student"""
    return StudentSupervisorService.assign_supervisor_to_student(db, assignment, current_user)

@router.get("/student/{student_number}", response_model=List[StudentSupervisorResponse])
def get_student_supervisors(
    student_number: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all supervisors for a specific student"""
    return StudentSupervisorService.get_student_supervisors(db, student_number, current_user)

@router.get("/supervisor/{supervisor_id}", response_model=List[StudentSupervisorResponse])
def get_supervisor_students(
    supervisor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all students for a specific supervisor"""
    return StudentSupervisorService.get_supervisor_students(db, supervisor_id, current_user)

@router.put("/{assignment_id}", response_model=StudentSupervisorResponse)
def update_supervisor_assignment(
    assignment_id: int,
    assignment_update: StudentSupervisorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a supervisor assignment"""
    return StudentSupervisorService.update_supervisor_assignment(db, assignment_id, assignment_update, current_user)

@router.delete("/{assignment_id}")
def remove_supervisor_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a supervisor assignment"""
    success = StudentSupervisorService.remove_supervisor_assignment(db, assignment_id, current_user)
    if success:
        return {"message": "Supervisor assignment removed successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove supervisor assignment")

@router.get("/", response_model=List[StudentSupervisorResponse])
def get_all_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all supervisor assignments (admin only)"""
    return StudentSupervisorService.get_all_assignments(db, current_user, skip, limit)
