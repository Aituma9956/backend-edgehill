from datetime import date
from app.models.timeline import Timeline as TimelineModel
from app.models.user import User
from app.schemas.timeline import TimelineStageEnum
from app.core.security import create_access_token, get_password_hash

def test_create_timeline(client, db_session):
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
    
    timeline_data = {
        "student_number": "S12345678",
        "stage": "proposal",
        "milestone_name": "Literature Review Complete",
        "planned_date": "2024-03-15",
        "description": "Complete comprehensive literature review",
        "notes": "Focus on recent advances in AI"
    }
    
    response = client.post("/api/v1/timelines/", json=timeline_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == timeline_data["student_number"]
    assert data["stage"] == timeline_data["stage"]
    assert data["milestone_name"] == timeline_data["milestone_name"]
    assert data["status"] == "pending"

def test_get_student_timeline(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    milestone1 = TimelineModel(
        student_number="S11111111",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Research Proposal",
        planned_date=date(2024, 2, 15),
        status="completed"
    )
    milestone2 = TimelineModel(
        student_number="S11111111",
        stage=TimelineStageEnum.PROGRESSION,
        milestone_name="Mid-year Review",
        planned_date=date(2024, 8, 15),
        status="pending"
    )
    db_session.add_all([milestone1, milestone2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/timelines/student/S11111111", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    milestone_names = [t["milestone_name"] for t in data]
    assert "Research Proposal" in milestone_names
    assert "Mid-year Review" in milestone_names

def test_get_timelines_with_filters(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    timeline1 = TimelineModel(
        student_number="S22222222",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Proposal Defense",
        status="completed"
    )
    timeline2 = TimelineModel(
        student_number="S33333333",
        stage=TimelineStageEnum.FINAL,
        milestone_name="Thesis Submission",
        status="pending"
    )
    db_session.add_all([timeline1, timeline2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/timelines/?stage=proposal", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage"] == "proposal"

    response = client.get("/api/v1/timelines/?status=pending", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"

def test_update_timeline(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    timeline = TimelineModel(
        student_number="S44444444",
        stage=TimelineStageEnum.PROGRESSION,
        milestone_name="Annual Review",
        planned_date=date(2024, 6, 15),
        status="pending"
    )
    db_session.add(timeline)
    db_session.commit()
    db_session.refresh(timeline)
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "actual_date": "2024-06-20",
        "status": "completed",
        "notes": "Successfully completed annual review"
    }
    
    response = client.put(f"/api/v1/timelines/{timeline.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "completed"
    assert data["notes"] == "Successfully completed annual review"

def test_complete_timeline_milestone(client, db_session):
    student_user = User(
        username="S55555555",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    timeline = TimelineModel(
        student_number="S55555555",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Draft Proposal",
        planned_date=date(2024, 4, 15),
        status="pending"
    )
    db_session.add(timeline)
    db_session.commit()
    db_session.refresh(timeline)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    completion_data = {
        "actual_date": "2024-04-12",
        "notes": "Submitted draft proposal to supervisor"
    }
    
    response = client.put(
        f"/api/v1/timelines/{timeline.id}/complete",
        params=completion_data,
        headers=headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "completed"

def test_delete_timeline(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    timeline = TimelineModel(
        student_number="S66666666",
        stage=TimelineStageEnum.FINAL,
        milestone_name="Obsolete Milestone",
        status="pending"
    )
    db_session.add(timeline)
    db_session.commit()
    db_session.refresh(timeline)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.delete(f"/api/v1/timelines/{timeline.id}", headers=headers)
    assert response.status_code == 200
    assert "Timeline milestone deleted successfully" in response.json()["message"]

    response = client.get(f"/api/v1/timelines/{timeline.id}", headers=headers)
    assert response.status_code == 404

def test_student_access_own_timeline(client, db_session):
    student_user = User(
        username="S77777777",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    timeline = TimelineModel(
        student_number="S77777777",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="My Milestone",
        status="pending"
    )
    db_session.add(timeline)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/timelines/student/S77777777", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["student_number"] == "S77777777"

def test_student_cannot_access_other_timeline(client, db_session):
    student_user = User(
        username="S88888888",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    timeline = TimelineModel(
        student_number="S99999999",
        stage=TimelineStageEnum.PROPOSAL,
        milestone_name="Other Student Milestone",
        status="pending"
    )
    db_session.add(timeline)
    db_session.commit()
    db_session.refresh(timeline)
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/timelines/student/S99999999", headers=headers)
    assert response.status_code == 403

    response = client.get(f"/api/v1/timelines/{timeline.id}", headers=headers)
    assert response.status_code == 403

def test_timeline_unauthorized_creation(client, db_session):
    """Test that unauthorized users cannot create timelines"""
    timeline_data = {
        "student_number": "S12121212",
        "stage": "proposal",
        "milestone_name": "Unauthorized Milestone"
    }

    response = client.post("/api/v1/timelines/", json=timeline_data)
    assert response.status_code == 403

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
    
    response = client.post("/api/v1/timelines/", json=timeline_data, headers=headers)
    assert response.status_code == 403

def test_timeline_pagination(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    timelines = []
    for i in range(5):
        timeline = TimelineModel(
            student_number=f"S{str(i).zfill(8)}",
            stage=TimelineStageEnum.PROPOSAL,
            milestone_name=f"Milestone {i}",
            status="pending"
        )
        timelines.append(timeline)
    
    db_session.add_all(timelines)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/timelines/?skip=0&limit=3", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    response = client.get("/api/v1/timelines/?skip=3&limit=3", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
