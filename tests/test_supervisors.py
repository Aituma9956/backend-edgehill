from app.models.supervisor import Supervisor
from app.models.user import User
from app.core.security import create_access_token, get_password_hash

def test_create_supervisor(client, db_session):
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
    
    supervisor_data = {
        "supervisor_name": "Dr. Jane Smith",
        "email": "jane.smith@edgehill.ac.uk",
        "department": "Computer Science",
        "supervisor_notes": "AI specialist"
    }
    
    response = client.post("/api/v1/supervisors/", json=supervisor_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["supervisor_name"] == supervisor_data["supervisor_name"]
    assert data["email"] == supervisor_data["email"]
    assert data["department"] == supervisor_data["department"]

def test_get_supervisors(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    supervisor1 = Supervisor(
        supervisor_name="Dr. Alice Johnson",
        email="alice.johnson@edgehill.ac.uk",
        department="Mathematics"
    )
    supervisor2 = Supervisor(
        supervisor_name="Prof. Bob Wilson",
        email="bob.wilson@edgehill.ac.uk",
        department="Physics"
    )
    db_session.add_all([supervisor1, supervisor2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/supervisors/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    supervisor_names = [s["supervisor_name"] for s in data]
    assert "Dr. Alice Johnson" in supervisor_names
    assert "Prof. Bob Wilson" in supervisor_names

def test_get_supervisor_by_id(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    supervisor = Supervisor(
        supervisor_name="Dr. Charlie Brown",
        email="charlie.brown@edgehill.ac.uk",
        department="Chemistry"
    )
    db_session.add(supervisor)
    db_session.commit()
    db_session.refresh(supervisor)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get(f"/api/v1/supervisors/{supervisor.supervisor_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["supervisor_name"] == "Dr. Charlie Brown"
    assert data["email"] == "charlie.brown@edgehill.ac.uk"
    assert data["department"] == "Chemistry"

def test_update_supervisor(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    supervisor = Supervisor(
        supervisor_name="Dr. David Lee",
        email="david.lee@edgehill.ac.uk",
        department="Biology"
    )
    db_session.add(supervisor)
    db_session.commit()
    db_session.refresh(supervisor)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "supervisor_name": "Prof. David Lee",
        "supervisor_notes": "Molecular biology expert"
    }
    
    response = client.put(f"/api/v1/supervisors/{supervisor.supervisor_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["supervisor_name"] == "Prof. David Lee"
    assert data["supervisor_notes"] == "Molecular biology expert"

def test_search_supervisors(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    supervisor1 = Supervisor(
        supervisor_name="Dr. Machine Learning",
        email="ml@edgehill.ac.uk",
        department="Computer Science"
    )
    supervisor2 = Supervisor(
        supervisor_name="Dr. Statistics Expert",
        email="stats@edgehill.ac.uk",
        department="Mathematics"
    )
    db_session.add_all([supervisor1, supervisor2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/supervisors/?department=Computer Science", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["department"] == "Computer Science"

    response = client.get("/api/v1/supervisors/?name=Machine", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "Machine Learning" in data[0]["supervisor_name"]

def test_supervisor_unauthorized_access(client, db_session):
    """Test that unauthorized users cannot create/modify supervisors"""
    supervisor_data = {
        "supervisor_name": "Unauthorized Supervisor",
        "email": "unauthorized@edgehill.ac.uk",
        "department": "Unknown"
    }

    response = client.post("/api/v1/supervisors/", json=supervisor_data)
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
    
    response = client.post("/api/v1/supervisors/", json=supervisor_data, headers=headers)
    assert response.status_code == 403

def test_supervisor_not_found(client, db_session):
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
    
    response = client.get("/api/v1/supervisors/99999", headers=headers)
    assert response.status_code == 404
