from app.models.submission import Submission as SubmissionModel
from app.models.user import User
from app.schemas.submission import SubmissionTypeEnum, SubmissionStatusEnum
from app.core.security import create_access_token, get_password_hash

def test_create_submission(client, db_session):
    student_user = User(
        username="S12345678",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    submission_data = {
        "student_number": "S12345678",
        "submission_type": "thesis",
        "title": "AI Applications in Healthcare",
        "description": "Final PhD thesis submission",
        "review_deadline": "2024-08-31"
    }
    
    response = client.post("/api/v1/submissions/", json=submission_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == submission_data["student_number"]
    assert data["submission_type"] == submission_data["submission_type"]
    assert data["title"] == submission_data["title"]
    assert data["status"] == "draft"

def test_get_submissions(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S11111111",
        submission_type=SubmissionTypeEnum.REGISTRATION,
        title="Research Proposal: Machine Learning",
        status=SubmissionStatusEnum.SUBMITTED
    )
    submission2 = SubmissionModel(
        student_number="S22222222",
        submission_type="thesis",
        title="Deep Learning in Computer Vision",
        status="under_review"
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/submissions/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    titles = [s["title"] for s in data]
    assert "Research Proposal: Machine Learning" in titles
    assert "Deep Learning in Computer Vision" in titles

def test_get_submission_by_id(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S33333333",
        submission_type="chapter",
        title="Chapter 3: Methodology",
        description="Detailed methodology chapter",
        status="submitted"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/submissions/{submission.id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Chapter 3: Methodology"
    assert data["submission_type"] == "chapter"

def test_update_submission(client, db_session):
    student_user = User(
        username="S44444444",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S44444444",
        submission_type="proposal",
        title="Draft Proposal",
        status="draft"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "title": "Final Research Proposal",
        "description": "Updated and finalized research proposal",
        "status": "submitted"
    }
    
    response = client.put(f"/api/v1/submissions/{submission.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Final Research Proposal"
    assert data["status"] == "submitted"

def test_file_upload_submission(client, db_session):
    student_user = User(
        username="S55555555",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S55555555",
        submission_type="thesis",
        title="PhD Thesis",
        status="draft"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    files = {
        "file": ("thesis.pdf", b"fake pdf content", "application/pdf")
    }
    
    response = client.post(
        f"/api/v1/submissions/{submission.id}/upload",
        files=files,
        headers=headers
    )
    assert response.status_code == 200
    assert "File uploaded successfully" in response.json()["message"]

def test_supervisor_review_submission(client, db_session):
    supervisor_user = User(
        username="supervisor",
        email="supervisor@edgehill.ac.uk",
        hashed_password=get_password_hash("supervisor123"),
        role="supervisor"
    )
    db_session.add(supervisor_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S66666666",
        submission_type="chapter",
        title="Chapter 1: Introduction",
        status="submitted"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": supervisor_user.username, "role": supervisor_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    review_data = {
        "status": "approved",
        "review_comments": "Excellent introduction chapter. Well structured and comprehensive."
    }
    
    response = client.put(
        f"/api/v1/submissions/{submission.id}/review",
        json=review_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"
    assert data["review_comments"] == review_data["review_comments"]

def test_submission_requires_revision(client, db_session):
    supervisor_user = User(
        username="supervisor",
        email="supervisor@edgehill.ac.uk",
        hashed_password=get_password_hash("supervisor123"),
        role="supervisor"
    )
    db_session.add(supervisor_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S77777777",
        submission_type="proposal",
        title="Research Proposal",
        status="submitted"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": supervisor_user.username, "role": supervisor_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    review_data = {
        "status": "revision_required",
        "review_comments": "Good start but needs more detail in methodology section. Please revise and resubmit."
    }
    
    response = client.put(
        f"/api/v1/submissions/{submission.id}/review",
        json=review_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "revision_required"

def test_filter_submissions_by_type(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S10101010",
        submission_type="proposal",
        title="Research Proposal",
        status="submitted"
    )
    submission2 = SubmissionModel(
        student_number="S20202020",
        submission_type="thesis",
        title="Final Thesis",
        status="under_review"
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/submissions/?submission_type=proposal", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["submission_type"] == "proposal"

def test_filter_submissions_by_status(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S30303030",
        submission_type="chapter",
        title="Chapter Draft",
        status="draft"
    )
    submission2 = SubmissionModel(
        student_number="S40404040",
        submission_type="chapter",
        title="Chapter Final",
        status="approved"
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/submissions/?status=approved", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "approved"

def test_student_access_own_submissions(client, db_session):
    student_user = User(
        username="S88888888",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    submission1 = SubmissionModel(
        student_number="S88888888",
        submission_type="proposal",
        title="My Proposal",
        status="draft"
    )
    submission2 = SubmissionModel(
        student_number="S88888888",
        submission_type="chapter",
        title="My Chapter",
        status="submitted"
    )
    db_session.add_all([submission1, submission2])
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/submissions/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    for submission in data:
        assert submission["student_number"] == "S88888888"

def test_student_cannot_access_other_submissions(client, db_session):
    student_user = User(
        username="S99999999",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    submission = SubmissionModel(
        student_number="S12121212",
        submission_type="thesis",
        title="Other Student Thesis",
        status="submitted"
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/submissions/{submission.id}", headers=headers)
    assert response.status_code == 403

def test_submission_unauthorized_creation(client):
    submission_data = {
        "student_number": "S13131313",
        "submission_type": "proposal",
        "title": "Unauthorized Submission"
    }

    response = client.post("/api/v1/submissions/", json=submission_data)
    assert response.status_code == 401

def test_submission_pagination(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    submissions = []
    for i in range(5):
        submission = SubmissionModel(
            student_number=f"S{str(i).zfill(8)}",
            submission_type="chapter",
            title=f"Chapter {i}",
            status="draft"
        )
        submissions.append(submission)
    
    db_session.add_all(submissions)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/submissions/?skip=0&limit=3", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    response = client.get("/api/v1/submissions/?skip=3&limit=3", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_submission_with_deadline(client, db_session):
    student_user = User(
        username="S14141414",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    submission_data = {
        "student_number": "S14141414",
        "submission_type": "thesis",
        "title": "Final Thesis with Deadline",
        "review_deadline": "2024-12-31"
    }
    
    response = client.post("/api/v1/submissions/", json=submission_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["review_deadline"] is not None
