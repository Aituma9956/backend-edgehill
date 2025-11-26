from app.models.viva_team import VivaTeam
from app.models.supervisor import Supervisor
from app.models.user import User
from app.schemas.viva_team import VivaStageEnum, VivaStatusEnum
from app.core.security import create_access_token, get_password_hash

def test_create_viva_team(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()
    db_session.refresh(dos_user)

    supervisor1 = Supervisor(
        supervisor_name="Dr. Internal One",
        email="internal1@edgehill.ac.uk"
    )
    supervisor2 = Supervisor(
        supervisor_name="Dr. Internal Two",
        email="internal2@edgehill.ac.uk"
    )
    db_session.add_all([supervisor1, supervisor2])
    db_session.commit()
    db_session.refresh(supervisor1)
    db_session.refresh(supervisor2)
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    viva_team_data = {
        "student_number": "S12345678",
        "stage": "final",
        "internal_examiner_1_id": supervisor1.supervisor_id,
        "internal_examiner_2_id": supervisor2.supervisor_id,
        "external_examiner_name": "Prof. External Smith",
        "external_examiner_email": "external@university.ac.uk",
        "external_examiner_institution": "Other University",
        "proposed_date": "2024-06-15",
        "location": "Room 101"
    }
    
    response = client.post("/api/v1/viva-teams/", json=viva_team_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == viva_team_data["student_number"]
    assert data["stage"] == viva_team_data["stage"]
    assert data["status"] == "proposed"
    assert data["proposed_by"] == dos_user.id

def test_get_viva_teams(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    viva_team1 = VivaTeam(
        student_number="S11111111",
        stage=VivaStageEnum.REGISTRATION,
        status=VivaStatusEnum.PROPOSED,
        internal_examiner_1_id=1
    )
    viva_team2 = VivaTeam(
        student_number="S22222222",
        stage=VivaStageEnum.FINAL,
        status=VivaStatusEnum.APPROVED,
        internal_examiner_1_id=2
    )
    db_session.add_all([viva_team1, viva_team2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/viva-teams/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    student_numbers = [vt["student_number"] for vt in data]
    assert "S11111111" in student_numbers
    assert "S22222222" in student_numbers

def test_get_viva_team_by_id(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    viva_team = VivaTeam(
        student_number="S33333333",
        stage=VivaStageEnum.PROGRESSION,
        status=VivaStatusEnum.PROPOSED,
        internal_examiner_1_id=1,
        external_examiner_name="Prof. External"
    )
    db_session.add(viva_team)
    db_session.commit()
    db_session.refresh(viva_team)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/viva-teams/{viva_team.id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == "S33333333"
    assert data["stage"] == "progression"
    assert data["external_examiner_name"] == "Prof. External"

def test_update_viva_team(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    viva_team = VivaTeam(
        student_number="S44444444",
        stage=VivaStageEnum.FINAL,
        status=VivaStatusEnum.PROPOSED,
        internal_examiner_1_id=1
    )
    db_session.add(viva_team)
    db_session.commit()
    db_session.refresh(viva_team)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "status": "approved",
        "scheduled_date": "2024-07-15",
        "location": "Updated Room 202",
        "outcome_notes": "Approved by committee"
    }
    
    response = client.put(f"/api/v1/viva-teams/{viva_team.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "approved"
    assert data["location"] == "Updated Room 202"

def test_approve_viva_team(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    viva_team = VivaTeam(
        student_number="S55555555",
        stage=VivaStageEnum.FINAL,
        status=VivaStatusEnum.PROPOSED,
        internal_examiner_1_id=1
    )
    db_session.add(viva_team)
    db_session.commit()
    db_session.refresh(viva_team)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(f"/api/v1/viva-teams/{viva_team.id}/approve", headers=headers)
    assert response.status_code == 200
    assert "Viva team approved successfully" in response.json()["message"]

def test_schedule_viva(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    viva_team = VivaTeam(
        student_number="S66666666",
        stage=VivaStageEnum.FINAL,
        status=VivaStatusEnum.APPROVED,
        internal_examiner_1_id=1
    )
    db_session.add(viva_team)
    db_session.commit()
    db_session.refresh(viva_team)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    schedule_data = {
        "scheduled_date": "2024-08-15",
        "location": "Conference Room A"
    }
    
    response = client.post(
        f"/api/v1/viva-teams/{viva_team.id}/schedule", 
        json=schedule_data, 
        headers=headers
    )
    assert response.status_code == 200
    assert "Viva scheduled successfully" in response.json()["message"]

def test_filter_viva_teams_by_stage(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    viva_team1 = VivaTeam(
        student_number="S10101010",
        stage=VivaStageEnum.REGISTRATION,
        status=VivaStatusEnum.PROPOSED,
        internal_examiner_1_id=1
    )
    viva_team2 = VivaTeam(
        student_number="S20202020",
        stage=VivaStageEnum.FINAL,
        status=VivaStatusEnum.APPROVED,
        internal_examiner_1_id=2
    )
    db_session.add_all([viva_team1, viva_team2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/viva-teams/?stage=final", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["stage"] == "final"

def test_viva_team_unauthorized_access(client, db_session):
    viva_team_data = {
        "student_number": "S99999999",
        "stage": "final",
        "internal_examiner_1_id": 1
    }

    response = client.post("/api/v1/viva-teams/", json=viva_team_data)
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
    
    response = client.post("/api/v1/viva-teams/", json=viva_team_data, headers=headers)
    assert response.status_code == 403

def test_viva_team_not_found(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/viva-teams/99999", headers=headers)
    assert response.status_code == 404
