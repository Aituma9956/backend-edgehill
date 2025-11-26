from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from fastapi import HTTPException
from app.models.timeline import Timeline
from app.models.user import User
from app.schemas.timeline import TimelineCreate, TimelineUpdate, Timeline as TimelineSchema

class TimelineService:
    @staticmethod
    def create_timeline(db: Session, timeline: TimelineCreate) -> TimelineSchema:
        """Create a new timeline"""
        db_timeline = Timeline(**timeline.dict())
        db.add(db_timeline)
        db.commit()
        db.refresh(db_timeline)
        return TimelineSchema.from_orm(db_timeline)
    
    @staticmethod
    def get_student_timelines(db: Session, student_number: str, current_user: User) -> List[TimelineSchema]:
        """Get timelines for a student with authorization check"""
        if current_user.role == "student" and current_user.username != student_number:
            raise HTTPException(status_code=403, detail="Not authorized to view this timeline")
        
        timelines = db.query(Timeline).filter(Timeline.student_number == student_number).all()
        return [TimelineSchema.from_orm(timeline) for timeline in timelines]
    
    @staticmethod
    def get_timelines(db: Session, current_user: User, skip: int = 0, limit: int = 100, 
                     student_number: Optional[str] = None, stage: Optional[str] = None, 
                     status: Optional[str] = None) -> List[TimelineSchema]:
        """Get timelines with filtering and authorization"""
        query = db.query(Timeline)

        if student_number:
            query = query.filter(Timeline.student_number.ilike(f"%{student_number}%"))
        
        if stage:
            query = query.filter(Timeline.stage == stage)
        
        if status:
            query = query.filter(Timeline.status == status)

        if current_user.role == "student":
            query = query.filter(Timeline.student_number == current_user.username)
        
        timelines = query.offset(skip).limit(limit).all()
        return [TimelineSchema.from_orm(timeline) for timeline in timelines]
    
    @staticmethod
    def get_timeline_by_id(db: Session, timeline_id: int, current_user: User) -> TimelineSchema:
        """Get timeline by ID with authorization check"""
        timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            raise HTTPException(status_code=404, detail="Timeline not found")

        if current_user.role == "student" and timeline.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to view this timeline")
        
        return TimelineSchema.from_orm(timeline)
    
    @staticmethod
    def update_timeline(db: Session, timeline_id: int, timeline_update: TimelineUpdate) -> TimelineSchema:
        """Update timeline information"""
        db_timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not db_timeline:
            raise HTTPException(status_code=404, detail="Timeline not found")
        
        update_data = timeline_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_timeline, field, value)
        
        db.commit()
        db.refresh(db_timeline)
        return TimelineSchema.from_orm(db_timeline)
    
    @staticmethod
    def complete_milestone(db: Session, timeline_id: int, actual_date: date, current_user: User, notes: Optional[str] = None) -> TimelineSchema:
        """Complete a timeline milestone with authorization check"""
        timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            raise HTTPException(status_code=404, detail="Timeline not found")

        if current_user.role == "student" and timeline.student_number != current_user.username:
            raise HTTPException(status_code=403, detail="Not authorized to update this timeline")
        
        timeline.actual_date = actual_date
        timeline.status = "completed"
        if notes:
            timeline.notes = notes
        
        db.commit()
        db.refresh(timeline)
        return TimelineSchema.from_orm(timeline)
    
    @staticmethod
    def delete_timeline(db: Session, timeline_id: int) -> None:
        """Delete a timeline"""
        timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            raise HTTPException(status_code=404, detail="Timeline not found")
        
        db.delete(timeline)
        db.commit()
    
    @staticmethod
    def get_timelines_by_status(db: Session, status: str) -> List[Timeline]:
        """Get timelines by status"""
        return db.query(Timeline).filter(Timeline.status == status).all()
    
    @staticmethod
    def get_timelines_by_milestone(db: Session, milestone: str) -> List[Timeline]:
        """Get timelines by milestone"""
        return db.query(Timeline).filter(Timeline.milestone == milestone).all()
    
    @staticmethod
    def complete_milestone(db: Session, timeline_id: int, completion_notes: str = None) -> Optional[Timeline]:
        """Mark a milestone as completed"""
        timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            return None
        
        timeline.status = "completed"
        timeline.actual_date = datetime.now().date()
        timeline.completion_notes = completion_notes
        db.commit()
        db.refresh(timeline)
        return timeline
    
    @staticmethod
    def get_overdue_milestones(db: Session) -> List[Timeline]:
        """Get milestones that are overdue"""
        today = date.today()
        return db.query(Timeline).filter(
            Timeline.planned_date < today,
            Timeline.status == "pending"
        ).all()
    
    @staticmethod
    def get_upcoming_milestones(db: Session, days_ahead: int = 30) -> List[Timeline]:
        """Get milestones due in the next specified days"""
        from datetime import timedelta
        future_date = date.today() + timedelta(days=days_ahead)
        return db.query(Timeline).filter(
            Timeline.planned_date <= future_date,
            Timeline.planned_date >= date.today(),
            Timeline.status == "pending"
        ).all()
    
    @staticmethod
    def reschedule_milestone(db: Session, timeline_id: int, new_date: date, reason: str = None) -> Optional[Timeline]:
        """Reschedule a milestone"""
        timeline = db.query(Timeline).filter(Timeline.id == timeline_id).first()
        if not timeline:
            return None
        
        timeline.planned_date = new_date
        timeline.reschedule_reason = reason
        db.commit()
        db.refresh(timeline)
        return timeline
    
    @staticmethod
    def get_student_progress(db: Session, student_number: str) -> dict:
        """Get student's overall progress"""
        timelines = db.query(Timeline).filter(Timeline.student_number == student_number).all()
        
        total_milestones = len(timelines)
        completed = len([t for t in timelines if t.status == "completed"])
        pending = len([t for t in timelines if t.status == "pending"])
        overdue = len([t for t in timelines if t.status == "pending" and t.planned_date < date.today()])
        
        return {
            "total_milestones": total_milestones,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": (completed / total_milestones * 100) if total_milestones > 0 else 0
        }
    
    @staticmethod
    def create_default_phd_timeline(db: Session, student_number: str, start_date: date) -> List[Timeline]:
        """Create default PhD timeline milestones"""
        from datetime import timedelta
        
        milestones = [
            {"milestone": "Initial Registration", "months_offset": 0},
            {"milestone": "Supervisor Assignment", "months_offset": 1},
            {"milestone": "Research Proposal", "months_offset": 6},
            {"milestone": "Confirmation", "months_offset": 12},
            {"milestone": "First Year Review", "months_offset": 12},
            {"milestone": "Annual Review 2", "months_offset": 24},
            {"milestone": "Annual Review 3", "months_offset": 36},
            {"milestone": "Thesis Submission", "months_offset": 42},
            {"milestone": "Viva Voce", "months_offset": 45},
            {"milestone": "Final Submission", "months_offset": 48}
        ]
        
        created_timelines = []
        for milestone_info in milestones:
            planned_date = start_date + timedelta(days=milestone_info["months_offset"] * 30)
            timeline_data = {
                "student_number": student_number,
                "milestone": milestone_info["milestone"],
                "planned_date": planned_date,
                "status": "pending"
            }
            timeline = TimelineService.create_timeline(db, timeline_data)
            created_timelines.append(timeline)
        
        return created_timelines
