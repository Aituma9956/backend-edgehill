from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from app.models.registration import Registration
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.models.timeline import Timeline, TimelineStage
from app.models.appraisal import Appraisal, AppraisalStatus
from app.models.viva_team import VivaTeam, VivaStatus
from app.models.student import Student

class ReportService:
    @staticmethod
    def get_student_overview_report(db: Session) -> Dict[str, Any]:
        """Generate student overview report"""
        total_students = db.query(Registration).count()
        
        # Group by registration status
        by_status = db.query(
            Registration.registration_status,
            func.count(Registration.registration_id).label('count')
        ).group_by(Registration.registration_status).all()
        
        # Group by programme (from Student table)
        by_programme = db.query(
            Student.programme_of_study,
            func.count(Registration.registration_id).label('count')
        ).join(Registration, Student.student_number == Registration.student_number
        ).group_by(Student.programme_of_study).all()
        
        # Group by mode (Full-time/Part-time)
        by_mode = db.query(
            Student.mode,
            func.count(Registration.registration_id).label('count')
        ).join(Registration, Student.student_number == Registration.student_number
        ).group_by(Student.mode).all()
        
        return {
            "total_students": total_students,
            "by_programme": [{"programme": item.programme_of_study or "Unknown", "count": item.count} for item in by_programme],
            "by_mode": [{"mode": item.mode or "Unknown", "count": item.count} for item in by_mode],
            "by_status": [{"status": item.registration_status or "Unknown", "count": item.count} for item in by_status]
        }
    
    @staticmethod
    def get_supervisor_workload_report(db: Session) -> Dict[str, Any]:
        """Generate supervisor workload report"""
        # Note: The Registration model doesn't have supervisor fields
        # This would need to be implemented with a separate Supervisor-Student relationship table
        # For now, return basic registration data
        workload = db.query(
            Registration.registration_status,
            func.count(Registration.registration_id).label('student_count')
        ).filter(
            Registration.registration_status.in_(["active", "enrolled"])
        ).group_by(Registration.registration_status).all()
        
        total_active_students = sum(item.student_count for item in workload)
        
        return {
            "total_active_students": total_active_students,
            "workload_by_status": [
                {
                    "status": item.registration_status,
                    "student_count": item.student_count
                }
                for item in workload
            ]
        }
    
    @staticmethod
    def get_submission_analytics(db: Session, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Generate submission analytics report"""
        query = db.query(Submission)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    Submission.submission_date >= start_date,
                    Submission.submission_date <= end_date
                )
            )
        
        submissions = query.all()
        total_submissions = len(submissions)
        
        # Group by type
        by_type = {}
        for submission in submissions:
            by_type[submission.submission_type] = by_type.get(submission.submission_type, 0) + 1
        
        # Group by status
        by_status = {}
        for submission in submissions:
            by_status[submission.status] = by_status.get(submission.status, 0) + 1
        
        return {
            "total_submissions": total_submissions,
            "by_type": [{"type": k.value if hasattr(k, 'value') else str(k), "count": v} for k, v in by_type.items()],
            "by_status": [{"status": k.value if hasattr(k, 'value') else str(k), "count": v} for k, v in by_status.items()]
        }
    
    @staticmethod
    def get_timeline_compliance_report(db: Session) -> Dict[str, Any]:
        """Generate timeline compliance report"""
        today = date.today()
        
        # On time completions
        on_time = db.query(Timeline).filter(
            and_(
                Timeline.status == "completed",
                Timeline.actual_date.isnot(None),
                Timeline.actual_date <= Timeline.planned_date
            )
        ).count()
        
        # Overdue completions
        overdue = db.query(Timeline).filter(
            and_(
                Timeline.status == "completed",
                Timeline.actual_date.isnot(None),
                Timeline.actual_date > Timeline.planned_date
            )
        ).count()
        
        # Pending milestones
        pending = db.query(Timeline).filter(Timeline.status == "pending").count()
        
        # Overdue pending
        overdue_pending = db.query(Timeline).filter(
            and_(
                Timeline.status == "pending",
                Timeline.planned_date < today
            )
        ).count()
        
        total_milestones = on_time + overdue + pending
        
        return {
            "on_time": on_time,
            "overdue": overdue,
            "pending": pending,
            "overdue_pending": overdue_pending,
            "total_milestones": total_milestones,
            "compliance_rate": (on_time / (on_time + overdue) * 100) if (on_time + overdue) > 0 else 0
        }
    
    @staticmethod
    def get_appraisal_completion_rates(db: Session, academic_year: str = None) -> Dict[str, Any]:
        """Generate appraisal completion rates report"""
        query = db.query(Appraisal)
        if academic_year:
            query = query.filter(Appraisal.academic_year == academic_year)
        
        appraisals = query.all()
        total = len(appraisals)
        
        # Group by status
        by_status = {}
        for appraisal in appraisals:
            by_status[appraisal.status] = by_status.get(appraisal.status, 0) + 1
        
        # Group by period
        by_period = {}
        for appraisal in appraisals:
            by_period[appraisal.appraisal_period] = by_period.get(appraisal.appraisal_period, 0) + 1
        
        completed = by_status.get(AppraisalStatus.APPROVED, 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        return {
            "completion_rate": completion_rate,
            "total_appraisals": total,
            "by_status": [{"status": k.value if hasattr(k, 'value') else str(k), "count": v} for k, v in by_status.items()],
            "by_period": [{"period": k.value if hasattr(k, 'value') else str(k), "count": v} for k, v in by_period.items()]
        }
    
    @staticmethod
    def get_programme_statistics(db: Session) -> Dict[str, Any]:
        """Generate programme statistics"""
        stats = db.query(
            Student.programme_of_study,
            Student.mode,
            func.count(Registration.registration_id).label('student_count')
        ).join(Registration, Student.student_number == Registration.student_number
        ).group_by(
            Student.programme_of_study,
            Student.mode
        ).all()
        
        programme_data = [
            {
                "programme": item.programme_of_study or "Unknown",
                "mode": item.mode or "Unknown", 
                "student_count": item.student_count
            }
            for item in stats
        ]
        
        return {
            "total_programmes": len(programme_data),
            "programme_statistics": programme_data
        }
    
    @staticmethod
    def get_department_dashboard(db: Session) -> Dict[str, Any]:
        """Generate department dashboard data"""
        # Active students
        active_students = db.query(Registration).filter(Registration.registration_status.in_(["active", "enrolled"])).count()
        
        # Pending submissions
        pending_submissions = db.query(Submission).filter(
            Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.UNDER_REVIEW])
        ).count()
        
        # Overdue milestones
        today = date.today()
        overdue_milestones = db.query(Timeline).filter(
            and_(
                Timeline.status == "pending",
                Timeline.planned_date < today
            )
        ).count()
        
        # Pending appraisals
        pending_appraisals = db.query(Appraisal).filter(
            Appraisal.status.in_([AppraisalStatus.PENDING, AppraisalStatus.STUDENT_SUBMITTED])
        ).count()
        
        # Pending viva teams
        pending_viva_teams = db.query(VivaTeam).filter(VivaTeam.status == VivaStatus.PROPOSED).count()
        
        return {
            "active_students": active_students,
            "pending_submissions": pending_submissions,
            "overdue_milestones": overdue_milestones,
            "pending_appraisals": pending_appraisals,
            "pending_viva_teams": pending_viva_teams
        }
    
    @staticmethod
    def get_weekly_activity_report(db: Session) -> Dict[str, Any]:
        """Generate weekly activity report"""
        week_ago = datetime.now() - timedelta(days=7)
        
        # New registrations this week
        new_registrations = db.query(Registration).filter(
            Registration.created_date >= week_ago
        ).count()
        
        # Submissions this week
        submissions_this_week = db.query(Submission).filter(
            Submission.submission_date >= week_ago
        ).count()
        
        # Completed milestones this week
        completed_milestones = db.query(Timeline).filter(
            and_(
                Timeline.status == "completed",
                Timeline.actual_date >= week_ago.date()
            )
        ).count()
        
        # Upcoming deadlines (next week)
        next_week = datetime.now() + timedelta(days=7)
        upcoming_deadlines = db.query(Timeline).filter(
            and_(
                Timeline.status == "pending",
                Timeline.planned_date <= next_week.date(),
                Timeline.planned_date >= date.today()
            )
        ).count()
        
        return {
            "new_registrations": new_registrations,
            "submissions_this_week": submissions_this_week,
            "completed_milestones": completed_milestones,
            "upcoming_deadlines": upcoming_deadlines
        }
    
    @staticmethod
    def get_custom_report(db: Session, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate custom report based on filters"""
        query = db.query(Registration).join(Student, Registration.student_number == Student.student_number)
        
        if filters.get("programme"):
            query = query.filter(Student.programme_of_study == filters["programme"])
        
        if filters.get("mode"):
            query = query.filter(Student.mode == filters["mode"])
        
        if filters.get("status"):
            query = query.filter(Registration.registration_status == filters["status"])
        
        if filters.get("cohort"):
            query = query.filter(Student.cohort == filters["cohort"])
        
        registrations = query.all()
        
        report_data = [
            {
                "student_number": reg.student_number,
                "programme": reg.student.programme_of_study or "Unknown",
                "mode": reg.student.mode or "Unknown",
                "status": reg.registration_status or "Unknown",
                "cohort": reg.student.cohort or "Unknown",
                "created_date": reg.created_date.isoformat() if reg.created_date else None
            }
            for reg in registrations
        ]
        
        return {
            "total_records": len(report_data),
            "filters_applied": filters,
            "data": report_data
        }
