from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from datetime import datetime
import os
import shutil
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionUpdate, Submission as SubmissionSchema

class SubmissionService:
    @staticmethod
    def create_submission(db: Session, submission: SubmissionCreate, current_user: User) -> SubmissionSchema:
        """Create a new submission"""
        # Students can only create submissions for themselves
        if current_user.role == "student" and submission.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to create submission for another student")
        
        submission_data = submission.dict()
        
        # Convert schema enums to model enums if needed
        if 'submission_type' in submission_data:
            type_value = submission_data['submission_type']
            if hasattr(type_value, 'value'):
                submission_data['submission_type'] = SubmissionType(type_value.value)
            else:
                submission_data['submission_type'] = SubmissionType(type_value)
        
        submission_data.update({
            "submission_date": datetime.now(),
            "status": SubmissionStatus.DRAFT
        })
        
        db_submission = Submission(**submission_data)
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        return SubmissionSchema.from_orm(db_submission)
    
    @staticmethod
    def get_submissions(db: Session, current_user: User, student_number: Optional[str] = None,
                       submission_type: Optional[str] = None, status: Optional[str] = None) -> List[SubmissionSchema]:
        """Get submissions with filtering and authorization"""
        query = db.query(Submission)

        if student_number:
            query = query.filter(Submission.student_number.ilike(f"%{student_number}%"))
        
        if submission_type:
            # Convert string to enum if needed
            try:
                type_enum = SubmissionType(submission_type) if isinstance(submission_type, str) else submission_type
                query = query.filter(Submission.submission_type == type_enum)
            except ValueError:
                pass  # Invalid submission type, ignore filter
            
        if status:
            # Convert string to enum if needed
            try:
                status_enum = SubmissionStatus(status) if isinstance(status, str) else status
                query = query.filter(Submission.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter

        # Students can only see their own submissions
        if current_user.role == "student":
            query = query.filter(Submission.student_number == current_user.username)
        
        submissions = query.all()
        return [SubmissionSchema.from_orm(submission) for submission in submissions]
    
    @staticmethod
    def get_submission_by_id(db: Session, submission_id: int, current_user: User) -> SubmissionSchema:
        """Get submission by ID with authorization check"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Students can only view their own submissions
        if current_user.role == "student" and submission.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view this submission")
        
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    async def upload_file(db: Session, submission_id: int, file: UploadFile, current_user: User) -> SubmissionSchema:
        """Upload file for a submission with authorization check"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Students can only upload files to their own submissions
        if current_user.role == "student" and submission.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to upload file to this submission")
        
        # Create uploads directory if it doesn't exist
        upload_dir = f"uploads/submissions/{submission_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = f"{upload_dir}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update submission with file information
        submission.file_path = file_path
        submission.file_name = file.filename
        submission.file_size = os.path.getsize(file_path)
        submission.submission_date = datetime.now()  # Updated field name
        
        db.commit()
        db.refresh(submission)
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    def update_submission(db: Session, submission_id: int, submission_update: SubmissionUpdate, current_user: User) -> SubmissionSchema:
        """Update submission with authorization check"""
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Students can only update their own submissions and only if draft
        if current_user.role == "student":
            if submission.student_number != current_user.username:
                raise HTTPException(status_code=403, detail="Not authorized to update this submission")
            if submission.status != SubmissionStatus.DRAFT:
                raise HTTPException(status_code=400, detail="Cannot update submission that is not in draft status")
        
        update_data = submission_update.dict(exclude_unset=True)
        
        # Convert schema enums to model enums if present
        if 'submission_type' in update_data:
            type_value = update_data['submission_type']
            if hasattr(type_value, 'value'):
                update_data['submission_type'] = SubmissionType(type_value.value)
            else:
                update_data['submission_type'] = SubmissionType(type_value)
                
        if 'status' in update_data:
            status_value = update_data['status']
            if hasattr(status_value, 'value'):
                update_data['status'] = SubmissionStatus(status_value.value)
            else:
                update_data['status'] = SubmissionStatus(status_value)
        
        for field, value in update_data.items():
            setattr(submission, field, value)
        
        submission.updated_date = datetime.now()  # Use the correct field name
        db.commit()
        db.refresh(submission)
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    def approve_submission(db: Session, submission_id: int, current_user: User) -> SubmissionSchema:
        """Approve a submission - only supervisors/admin can approve"""
        if current_user.role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to approve submissions")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission.status = SubmissionStatus.APPROVED
        submission.review_date = datetime.now()
        submission.reviewed_by = current_user.id  # Use user ID, not username
        
        db.commit()
        db.refresh(submission)
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    def reject_submission(db: Session, submission_id: int, reason: str, current_user: User) -> SubmissionSchema:
        """Reject a submission - only supervisors/admin can reject"""
        if current_user.role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to reject submissions")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission.status = SubmissionStatus.REJECTED
        submission.review_comments = reason  # Use review_comments field
        submission.review_date = datetime.now()
        submission.reviewed_by = current_user.id  # Use user ID, not username
        
        db.commit()
        db.refresh(submission)
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    def review_submission(db: Session, submission_id: int, review_data: dict, current_user: User) -> SubmissionSchema:
        """Review a submission - can approve, reject, or require revision"""
        if current_user.role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to review submissions")
        
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        status = review_data.get("status")
        review_comments = review_data.get("review_comments")
        
        if status:
            # Convert to enum if it's a string
            if isinstance(status, str):
                submission.status = SubmissionStatus(status)
            else:
                submission.status = status
        if review_comments:
            submission.review_comments = review_comments
        
        submission.review_date = datetime.now()
        submission.reviewed_by = current_user.id  # Use user ID, not username
        
        db.commit()
        db.refresh(submission)
        return SubmissionSchema.from_orm(submission)
    
    @staticmethod
    def get_student_submissions(db: Session, student_number: str, current_user: User) -> List[SubmissionSchema]:
        """Get all submissions for a specific student with authorization"""
        if current_user.role == "student" and current_user.username != student_number:
            raise HTTPException(status_code=403, detail="Not authorized to view submissions for another student")
        
        submissions = db.query(Submission).filter(Submission.student_number == student_number).all()
        return [SubmissionSchema.from_orm(submission) for submission in submissions]
    
    @staticmethod
    def get_pending_submissions(db: Session, current_user: User) -> List[SubmissionSchema]:
        """Get all pending submissions - for supervisors/admin only"""
        if current_user.role not in ["supervisor", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view pending submissions")
        
        submissions = db.query(Submission).filter(Submission.status == SubmissionStatus.SUBMITTED).all()  # Use SUBMITTED instead of pending
        return [SubmissionSchema.from_orm(submission) for submission in submissions]
    
    @staticmethod
    def get_submissions_by_type(db: Session, submission_type: str, current_user: User) -> List[SubmissionSchema]:
        """Get submissions by type with authorization"""
        # Convert string to enum if needed
        try:
            type_enum = SubmissionType(submission_type) if isinstance(submission_type, str) else submission_type
            query = db.query(Submission).filter(Submission.submission_type == type_enum)
        except ValueError:
            # Invalid submission type, return empty list
            return []
        
        # Students can only see their own submissions
        if current_user.role == "student":
            query = query.filter(Submission.student_number == current_user.username)
        
        submissions = query.all()
        return [SubmissionSchema.from_orm(submission) for submission in submissions]
