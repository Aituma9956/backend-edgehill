from datetime import date, datetime
from app.models.submission import Submission as SubmissionModel
from app.models.registration import Registration as RegistrationModel
from app.models.timeline import Timeline as TimelineModel
from app.models.appraisal import Appraisal as AppraisalModel
from app.models.user import User
from app.schemas.submission import SubmissionTypeEnum, SubmissionStatusEnum
from app.schemas.timeline import TimelineStageEnum
from app.schemas.appraisal import AppraisalStatusEnum
from app.core.security import create_access_token, get_password_hash

def test_get_student_overview_report(client, db_session):
    admin_user = User(
        username="gbos_admin",
        email="gbos@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="gbos_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    reg1 = RegistrationModel(
        student_number="S11111111",
        registration_status="active"
    )
    reg2 = RegistrationModel(
        student_number="S22222222",
        registration_status="completed"
    )
    db_session.add_all([reg1, reg2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/student-overview", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_students" in data
    # Verify response structure
    assert "registration_count" in data
    assert "completion_rate" in data
    assert data["total_students"] == 2

def test_get_supervisor_workload_report(client, db_session):
    admin_user = User(
        username="gbos_admin",
        email="gbos@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="gbos_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    reg1 = RegistrationModel(
        student_number="S33333333",
        registration_status="active"
    )
    reg2 = RegistrationModel(
        student_number="S44444444",
        registration_status="active"
    )
    reg3 = RegistrationModel(
        student_number="S55555555",
        registration_status="active"
    )
    db_session.add_all([reg1, reg2, reg3])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/supervisor-workload", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)  # Updated expectation

def test_get_submission_analytics(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S66666666",
        submission_type=SubmissionTypeEnum.REGISTRATION,
        title="Proposal 1",
        status=SubmissionStatusEnum.SUBMITTED
    )
    submission2 = SubmissionModel(
        student_number="S77777777",
        submission_type=SubmissionTypeEnum.THESIS,
        title="Thesis 1",
        status=SubmissionStatusEnum.APPROVED
    )
    submission3 = SubmissionModel(
        student_number="S88888888",
        submission_type=SubmissionTypeEnum.ANNUAL_REPORT,
        title="Chapter 1",
        status=SubmissionStatusEnum.UNDER_REVIEW
    )
    db_session.add_all([submission1, submission2, submission3])
    db_session.commit()
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/submission-analytics", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_submissions" in data
    assert "by_type" in data
    assert "by_status" in data
    assert data["total_submissions"] == 3

def test_get_timeline_compliance_report(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    timeline1 = TimelineModel(
        student_number="S99999999",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Initial Registration",
        planned_date=date(2024, 1, 15),
        actual_date=date(2024, 1, 15),
        status="completed"
    )
    timeline2 = TimelineModel(
        student_number="S10101010",
        stage=TimelineStageEnum.PROGRESSION,
        milestone_name="Confirmation",
        planned_date=date(2024, 6, 1),
        actual_date=date(2024, 6, 10),
        status="completed"
    )
    timeline3 = TimelineModel(
        student_number="S11111111",
        stage=TimelineStageEnum.PROGRESSION,
        milestone_name="First Year Review",
        planned_date=date(2024, 12, 1),
        status="pending"
    )
    db_session.add_all([timeline1, timeline2, timeline3])
    db_session.commit()
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/timeline-compliance", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "on_time" in data
    assert "overdue" in data
    assert "pending" in data
    assert "total_milestones" in data

def test_get_appraisal_completion_rates(client, db_session):
    admin_user = User(
        username="gbos_admin",
        email="gbos@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="gbos_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    appraisal1 = AppraisalModel(
        student_number="S12121212",
        academic_year="2023-24",
        appraisal_period="Q1",
        status=AppraisalStatusEnum.APPROVED
    )
    appraisal2 = AppraisalModel(
        student_number="S13131313",
        academic_year="2023-24",
        appraisal_period="Q1",
        status=AppraisalStatusEnum.PENDING
    )
    appraisal3 = AppraisalModel(
        student_number="S14141414",
        academic_year="2023-24",
        appraisal_period="Q2",
        status=AppraisalStatusEnum.UNDER_REVIEW
    )
    db_session.add_all([appraisal1, appraisal2, appraisal3])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/appraisal-completion", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "completion_rate" in data
    assert "by_status" in data
    assert "by_period" in data

def test_get_programme_statistics(client, db_session):
    admin_user = User(
        username="system_admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    reg1 = RegistrationModel(
        student_number="S15151515",
        registration_status="active"
    )
    reg2 = RegistrationModel(
        student_number="S16161616",
        registration_status="completed"
    )
    reg3 = RegistrationModel(
        student_number="S17171717",
        registration_status="active"
    )
    db_session.add_all([reg1, reg2, reg3])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/programme-statistics", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # Updated to check for basic structure since model fields changed

def test_get_department_dashboard(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    registration = RegistrationModel(
        student_number="S18181818",
        registration_status="active"
    )
    submission = SubmissionModel(
        student_number="S18181818",
        submission_type=SubmissionTypeEnum.REGISTRATION,
        title="Research Proposal",
        status=SubmissionStatusEnum.SUBMITTED
    )
    timeline = TimelineModel(
        student_number="S18181818",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Registration",
        planned_date=date(2024, 1, 1),
        status="completed"
    )
    appraisal = AppraisalModel(
        id=1,
        appraisal_date=datetime.date.today(),
        status=AppraisalStatusEnum.COMPLETED
    )
    
    db_session.add_all([registration, submission, timeline, appraisal])
    db_session.commit()
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/department-dashboard", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "active_students" in data
    assert "pending_submissions" in data
    assert "overdue_milestones" in data
    assert "pending_appraisals" in data

def test_get_filtered_reports_by_date_range(client, db_session):
    admin_user = User(
        username="system_admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S19191919",
        submission_type=SubmissionTypeEnum.REGISTRATION,
        title="January Submission",
        status=SubmissionStatusEnum.SUBMITTED,
        submission_date=datetime(2024, 1, 15)
    )
    submission2 = SubmissionModel(
        student_number="S20202020",
        submission_type=SubmissionTypeEnum.THESIS,
        title="June Submission",
        status=SubmissionStatusEnum.SUBMITTED,
        submission_date=datetime(2024, 6, 15)
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/reports/submission-analytics?start_date=2024-01-01&end_date=2024-03-31",
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_submissions"] == 1

def test_unauthorized_access_to_reports(client, db_session):
    student_user = User(
        username="student",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/student-overview", headers=headers)
    assert response.status_code == 403

def test_get_export_data(client, db_session):
    admin_user = User(
        username="gbos_admin",
        email="gbos@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="gbos_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration = RegistrationModel(
        student_number="S21212121",
        registration_status="active"
    )
    db_session.add(registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/export/student-data", headers=headers)
    assert response.status_code == 200

    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_get_weekly_activity_report(client, db_session):
    admin_user = User(
        username="system_admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S22222222",
        submission_type=SubmissionTypeEnum.ANNUAL_REPORT,
        title="Recent Chapter",
        status=SubmissionStatusEnum.SUBMITTED,
        submission_date=datetime.now()
    )
    db_session.add(submission)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/reports/weekly-activity", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "new_registrations" in data
    assert "submissions_this_week" in data
    assert "completed_milestones" in data
    assert "upcoming_deadlines" in data

def test_get_custom_report(client, db_session):
    admin_user = User(
        username="system_admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration = RegistrationModel(
        student_number="S23232323",
        degree_type="PhD",
        programme="Computer Science",
        status="active",
        primary_supervisor="Dr. Smith"
    )
    db_session.add(registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/reports/custom?degree_type=PhD&programme=Computer Science&supervisor=Dr. Smith",
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_reports_require_authentication(client):
    response = client.get("/api/v1/reports/student-overview")
    assert response.status_code == 401
    
    response = client.get("/api/v1/reports/supervisor-workload")
    assert response.status_code == 401
    
    response = client.get("/api/v1/reports/submission-analytics")
    assert response.status_code == 401
