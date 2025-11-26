from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles, get_current_active_user
from app.services.student_service import StudentService
from app.schemas.student import StudentCreate, StudentUpdate, Student

router = APIRouter()

@router.post("/", response_model=Student)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "academic_admin"]))
):
    # Check if student number already exists
    if StudentService.get_student_by_number(db, student.student_number):
        raise HTTPException(status_code=400, detail="Student number already exists")
    
    db_student = StudentService.create_student(db, student)
    return db_student

@router.get("/", response_model=List[Student])
def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    programme: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if search:
        return StudentService.search_students(db, search)
    
    if programme:
        return StudentService.get_students_by_programme(db, programme)

    if current_user.role == "student":
        # Students can only see their own record
        student = StudentService.get_student_by_number(db, current_user.username)
        return [student] if student else []
    
    # For other roles, return paginated list
    return StudentService.get_students(db, skip, limit)

@router.get("/{student_number}", response_model=Student)
def get_student(
    student_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    student = StudentService.get_student_by_number(db, student_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.role == "student" and student.student_number != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to view this student")
    
    return student

@router.put("/{student_number}", response_model=Student)
def update_student(
    student_number: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "academic_admin", "gbos_admin"]))
):
    return StudentService.update_student_by_number(db, student_number, student_update)

@router.delete("/{student_number}")
def delete_student(
    student_number: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin"]))
):
    student = StudentService.get_student_by_number(db, student_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    success = StudentService.delete_student(db, student.id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}
