from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import date
from app.db.session import get_db
from app.models.user import User
from app.core.dependencies import require_roles
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/student-overview")
def get_student_overview_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get student overview report with statistics"""
    return ReportService.get_student_overview_report(db)

@router.get("/supervisor-workload")
def get_supervisor_workload_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get supervisor workload report"""
    return ReportService.get_supervisor_workload_report(db)

@router.get("/submission-analytics")
def get_submission_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get submission analytics report"""
    return ReportService.get_submission_analytics(db, start_date, end_date)

@router.get("/timeline-compliance")
def get_timeline_compliance_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get timeline compliance report"""
    return ReportService.get_timeline_compliance_report(db)

@router.get("/appraisal-completion")
def get_appraisal_completion_rates(
    academic_year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get appraisal completion rates"""
    return ReportService.get_appraisal_completion_rates(db, academic_year)

@router.get("/programme-statistics")
def get_programme_statistics(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get programme statistics"""
    return ReportService.get_programme_statistics(db)

@router.get("/department-dashboard")
def get_department_dashboard(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get department dashboard data"""
    return ReportService.get_department_dashboard(db)

@router.get("/weekly-activity")
def get_weekly_activity_report(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get weekly activity report"""
    return ReportService.get_weekly_activity_report(db)

@router.get("/custom")
def get_custom_report(
    degree_type: Optional[str] = Query(None),
    programme: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    supervisor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin", "dos"]))
) -> Dict[str, Any]:
    """Get custom report with filters"""
    filters = {}
    if degree_type:
        filters["degree_type"] = degree_type
    if programme:
        filters["programme"] = programme
    if status:
        filters["status"] = status
    if supervisor:
        filters["supervisor"] = supervisor
    
    return ReportService.get_custom_report(db, filters)

@router.get("/export/student-data")
def export_student_data(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["system_admin", "gbos_admin"]))
):
    """Export student data as CSV"""
    # This would generate CSV data
    csv_content = "student_number,programme,status,supervisor\n"  # Header
    custom_report = ReportService.get_custom_report(db, {})
    
    for record in custom_report["data"]:
        csv_content += f"{record['student_number']},{record['programme']},{record['status']},{record.get('supervisor', '')}\n"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_data.csv"}
    )
