from app.models.appraisal import Appraisal as AppraisalModel
from app.models.user import User
from app.core.security import create_access_token, get_password_hash
from app.schemas.appraisal import AppraisalStatusEnum

def test_create_appraisal(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    appraisal_data = {
        "student_number": "S12345678",
        "academic_year": "2023-24",
        "appraisal_period": "Annual Review",
        "due_date": "2024-05-31"
    }
    
    response = client.post("/api/v1/appraisals/", json=appraisal_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == appraisal_data["student_number"]
    assert data["academic_year"] == appraisal_data["academic_year"]
    assert data["status"] == "pending"

def test_get_student_appraisals(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    appraisal1 = AppraisalModel(
        student_number="S11111111",
        academic_year="2022-23",
        appraisal_period="Year 1 Review",
        status="approved"
    )
    appraisal2 = AppraisalModel(
        student_number="S11111111",
        academic_year="2023-24",
        appraisal_period="Year 2 Review",
        status="pending"
    )
    db_session.add_all([appraisal1, appraisal2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/appraisals/student/S11111111", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    periods = [a["appraisal_period"] for a in data]
    assert "Year 1 Review" in periods
    assert "Year 2 Review" in periods

def test_student_submission(client, db_session):
    student_user = User(
        username="S22222222",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    existing_appraisal = AppraisalModel(
        student_id=1,
        supervisor_id=2,
        semester="Semester 1",
        year=2023,
        status=AppraisalStatusEnum.APPROVED
    )
    db_session.add(existing_appraisal)
    db_session.commit()
    db_session.refresh(existing_appraisal)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    submission_data = {
        "student_progress_report": "I have made significant progress in my research...",
        "student_achievements": "Published 2 papers, presented at 3 conferences",
        "student_challenges": "Data collection was more challenging than expected",
        "student_goals": "Complete data analysis by end of year",
        "student_development_needs": "Need more training in statistical analysis"
    }
    
    response = client.put(
        f"/api/v1/appraisals/{existing_appraisal.id}/student-submission",
        json=submission_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "student_submitted"
    assert data["student_progress_report"] == submission_data["student_progress_report"]

def test_dos_submission(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    appraisal = AppraisalModel(
        student_number="S33333333",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.STUDENT_SUBMITTED,
        student_progress_report="Student progress report..."
    )
    db_session.add(appraisal)
    db_session.commit()
    db_session.refresh(appraisal)
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    dos_data = {
        "dos_comments": "Student is making good progress overall",
        "dos_progress_rating": "satisfactory",
        "dos_recommendations": "Continue with current research direction"
    }
    
    response = client.put(
        f"/api/v1/appraisals/{appraisal.id}/dos-submission",
        json=dos_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "dos_submitted"
    assert data["dos_comments"] == dos_data["dos_comments"]

def test_review_appraisal(client, db_session):
    """Test reviewing and approving an appraisal"""
    reviewer_user = User(
        username="reviewer",
        email="reviewer@edgehill.ac.uk",
        hashed_password=get_password_hash("reviewer123"),
        role="gbos_admin"
    )
    db_session.add(reviewer_user)
    db_session.commit()
    db_session.refresh(reviewer_user)

    appraisal = AppraisalModel(
        student_number="S44444444",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.DOS_SUBMITTED,
        student_progress_report="Student report...",
        dos_comments="DoS comments..."
    )
    db_session.add(appraisal)
    db_session.commit()
    db_session.refresh(appraisal)
    
    token = create_access_token(data={"sub": reviewer_user.username, "role": reviewer_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    review_data = {
        "status": "approved",
        "reviewer_comments": "Appraisal is comprehensive and satisfactory",
        "action_required": False
    }
    
    response = client.put(
        f"/api/v1/appraisals/{appraisal.id}/review",
        json=review_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"
    assert data["reviewer_comments"] == review_data["reviewer_comments"]
    assert data["reviewer_id"] == reviewer_user.id

def test_appraisal_with_action_required(client, db_session):
    reviewer_user = User(
        username="reviewer",
        email="reviewer@edgehill.ac.uk",
        hashed_password=get_password_hash("reviewer123"),
        role="gbos_admin"
    )
    db_session.add(reviewer_user)
    db_session.commit()
    db_session.refresh(reviewer_user)
    
    appraisal = AppraisalModel(
        student_number="S55555555",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.DOS_SUBMITTED
    )
    db_session.add(appraisal)
    db_session.commit()
    db_session.refresh(appraisal)
    
    token = create_access_token(data={"sub": reviewer_user.username, "role": reviewer_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    review_data = {
        "status": "approved",
        "reviewer_comments": "Good progress but needs improvement in one area",
        "action_required": True,
        "action_description": "Student needs to improve literature review",
        "action_deadline": "2024-08-31"
    }
    
    response = client.put(
        f"/api/v1/appraisals/{appraisal.id}/review",
        json=review_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["action_required"] == True
    assert data["action_description"] == review_data["action_description"]

def test_unsatisfactory_appraisal(client, db_session):
    reviewer_user = User(
        username="reviewer",
        email="reviewer@edgehill.ac.uk",
        hashed_password=get_password_hash("reviewer123"),
        role="gbos_admin"
    )
    db_session.add(reviewer_user)
    db_session.commit()
    db_session.refresh(reviewer_user)

    appraisal = AppraisalModel(
        student_number="S66666666",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.DOS_SUBMITTED
    )
    db_session.add(appraisal)
    db_session.commit()
    db_session.refresh(appraisal)
    
    token = create_access_token(data={"sub": reviewer_user.username, "role": reviewer_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    review_data = {
        "status": "unsatisfactory",
        "reviewer_comments": "Insufficient progress demonstrated",
        "action_required": True,
        "action_description": "Student must resubmit with additional evidence",
        "action_deadline": "2024-07-31"
    }
    
    response = client.put(
        f"/api/v1/appraisals/{appraisal.id}/review",
        json=review_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "unsatisfactory"

def test_student_access_own_appraisal(client, db_session):
    student_user = User(
        username="S77777777",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    appraisal = AppraisalModel(
        student_number="S77777777",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.PENDING
    )
    db_session.add(appraisal)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/appraisals/student/S77777777", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["student_number"] == "S77777777"

def test_student_cannot_access_other_appraisal(client, db_session):
    student_user = User(
        username="S88888888",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/appraisals/student/S99999999", headers=headers)
    assert response.status_code == 403

def test_appraisal_unauthorized_creation(client, db_session):
    """Test that unauthorized users cannot create appraisals"""
    appraisal_data = {
        "student_number": "S12121212",
        "academic_year": "2023-24",
        "appraisal_period": "Annual Review"
    }

    response = client.post("/api/v1/appraisals/", json=appraisal_data)
    assert response.status_code == 401

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
    
    response = client.post("/api/v1/appraisals/", json=appraisal_data, headers=headers)
    assert response.status_code == 403

def test_appraisal_workflow_validation(client, db_session):
    student_user = User(
        username="S90909090",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    appraisal = AppraisalModel(
        student_number="S90909090",
        academic_year="2023-24",
        appraisal_period="Annual Review",
        status=AppraisalStatusEnum.PENDING
    )
    db_session.add(appraisal)
    db_session.commit()
    db_session.refresh(appraisal)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
 
    dos_data = {
        "dos_comments": "This should fail",
        "dos_progress_rating": "satisfactory"
    }
    
    response = client.put(
        f"/api/v1/appraisals/{appraisal.id}/dos-submission",
        json=dos_data,
        headers=headers
    )
    assert response.status_code == 403
