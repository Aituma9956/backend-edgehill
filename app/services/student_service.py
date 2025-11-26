from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from app.models.student import Student
from app.models.registration import Registration
from app.schemas.student import StudentCreate, StudentUpdate, Student as StudentSchema

class StudentService:
    @staticmethod
    def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[StudentSchema]:
        """Get list of students with pagination"""
        students = db.query(Student).offset(skip).limit(limit).all()
        return [StudentSchema.from_orm(student) for student in students]
    
    @staticmethod
    def get_student_by_number(db: Session, student_number: str) -> Optional[StudentSchema]:
        """Get student by student number"""
        student = db.query(Student).filter(Student.student_number == student_number).first()
        return StudentSchema.from_orm(student) if student else None
    
    @staticmethod
    def create_student(db: Session, student_data: StudentCreate) -> StudentSchema:
        """Create a new student"""
        student = Student(**student_data.dict())
        db.add(student)
        db.commit()
        db.refresh(student)
        return StudentSchema.from_orm(student)
    
    @staticmethod
    def update_student(db: Session, student_id: int, student_data: StudentUpdate) -> Optional[StudentSchema]:
        """Update student information"""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None
        
        update_data = student_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(student, key) and value is not None:
                setattr(student, key, value)
        
        db.commit()
        db.refresh(student)
        return StudentSchema.from_orm(student)
    
    @staticmethod
    def update_student_by_number(db: Session, student_number: str, student_update: StudentUpdate) -> StudentSchema:
        """Update a student by student number"""
        student = db.query(Student).filter(Student.student_number == student_number).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        update_data = student_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        db.commit()
        db.refresh(student)
        return StudentSchema.from_orm(student)
    
    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        """Delete a student"""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False
        
        db.delete(student)
        db.commit()
        return True
    
    @staticmethod
    def search_students(db: Session, query: str) -> List[StudentSchema]:
        """Search students by name or student number"""
        students = db.query(Student).filter(
            Student.forename.ilike(f"%{query}%") |
            Student.surname.ilike(f"%{query}%") |
            Student.student_number.ilike(f"%{query}%")
        ).all()
        return [StudentSchema.from_orm(student) for student in students]
    
    @staticmethod
    def get_students_by_supervisor(db: Session, supervisor_id: int) -> List[StudentSchema]:
        """Get students by supervisor"""
        students = db.query(Student).join(Registration).filter(
            Registration.primary_supervisor_id == supervisor_id
        ).all()
        return [StudentSchema.from_orm(student) for student in students]
    
    @staticmethod
    def get_students_by_programme(db: Session, programme: str) -> List[StudentSchema]:
        """Get students by programme"""
        students = db.query(Student).filter(
            Student.programme_of_study.ilike(f"%{programme}%")
        ).all()
        return [StudentSchema.from_orm(student) for student in students]
    
    @staticmethod
    def get_active_students(db: Session) -> List[StudentSchema]:
        """Get all active students"""
        students = db.query(Student).join(Registration).filter(
            Registration.status == "active"
        ).all()
        return [StudentSchema.from_orm(student) for student in students]
