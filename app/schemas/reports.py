from pydantic import BaseModel
from typing import Dict

class StudentSummaryReport(BaseModel):
    total_students: int
    international_students: int
    domestic_students: int
    by_cohort: Dict[str, int]
    by_programme: Dict[str, int]
    by_mode: Dict[str, int]

class RegistrationReport(BaseModel):
    total_registrations: int
    pending_registrations: int
    completed_registrations: int
    extensions_requested: int
    extensions_approved: int

class VivaReport(BaseModel):
    total_vivas: int
    proposed_vivas: int
    approved_vivas: int
    scheduled_vivas: int
    completed_vivas: int
    by_stage: Dict[str, int]
    by_outcome: Dict[str, int]

class AppraisalReport(BaseModel):
    total_appraisals: int
    pending_appraisals: int
    student_submitted: int
    dos_submitted: int
    approved_appraisals: int
    unsatisfactory_appraisals: int
    overdue_appraisals: int

class SubmissionReport(BaseModel):
    total_submissions: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    pending_review: int

class DashboardSummary(BaseModel):
    total_students: int
    total_registrations: int
    pending_vivas: int
    overdue_appraisals: int
    pending_submissions: int
    user_role: str
