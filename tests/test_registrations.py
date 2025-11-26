from datetime import date, timedelta
from app.models.registration import Registration
from app.models.student import Student
from app.models.user import User
from app.core.security import create_access_token, get_password_hash

def test_create_registration(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    student = Student(
        student_number="S12345678",
        forename="John",
        surname="Doe",
        programme_of_study="PhD"
    )
    db_session.add(student)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    registration_data = {
        "student_number": "S12345678",
        "registration_status": "pending",
        "original_registration_deadline": "2024-12-31"
    }
    
    response = client.post("/api/v1/registrations/", json=registration_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == registration_data["student_number"]
    assert data["registration_status"] == registration_data["registration_status"]

def test_get_registrations(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration1 = Registration(
        student_number="S11111111",
        registration_status="approved",
        original_registration_deadline=date(2024, 12, 31)
    )
    registration2 = Registration(
        student_number="S22222222",
        registration_status="pending",
        original_registration_deadline=date(2025, 6, 30)
    )
    db_session.add_all([registration1, registration2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/registrations/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    student_numbers = [r["student_number"] for r in data]
    assert "S11111111" in student_numbers
    assert "S22222222" in student_numbers

def test_get_registration_by_student(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration = Registration(
        student_number="S33333333",
        registration_status="approved",
        original_registration_deadline=date(2024, 12, 31)
    )
    db_session.add(registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/registrations/student/S33333333", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == "S33333333"
    assert data["registration_status"] == "approved"

def test_update_registration(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration = Registration(
        student_number="S44444444",
        registration_status="pending",
        original_registration_deadline=date(2024, 12, 31)
    )
    db_session.add(registration)
    db_session.commit()
    db_session.refresh(registration)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "registration_status": "approved",
        "revised_registration_deadline": "2025-01-31"
    }
    
    response = client.put(f"/api/v1/registrations/{registration.registration_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["registration_status"] == "approved"

def test_request_extension(client, db_session):
    dos_user = User(
        username="dos",
        email="dos@edgehill.ac.uk",
        hashed_password=get_password_hash("dos123"),
        role="dos"
    )
    db_session.add(dos_user)
    db_session.commit()

    registration = Registration(
        student_number="S55555555",
        registration_status="approved",
        original_registration_deadline=date(2024, 12, 31)
    )
    db_session.add(registration)
    db_session.commit()
    db_session.refresh(registration)
    
    token = create_access_token(data={"sub": dos_user.username, "role": dos_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        f"/api/v1/registrations/{registration.registration_id}/extension",
        params={"extension_days": 30, "reason": "Research complexity"},
        headers=headers
    )
    assert response.status_code == 200
    assert "Extension request submitted successfully" in response.json()["message"]

def test_approve_extension(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration = Registration(
        student_number="S66666666",
        registration_status="approved",
        original_registration_deadline=date(2024, 12, 31),
        registration_extension_request_date=date.today(),
        registration_extension_length_days=30
    )
    db_session.add(registration)
    db_session.commit()
    db_session.refresh(registration)
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        f"/api/v1/registrations/{registration.registration_id}/extension/approve",
        headers=headers
    )
    assert response.status_code == 200
    assert "Extension approved successfully" in response.json()["message"]

def test_student_access_own_registration(client, db_session):
    student_user = User(
        username="S77777777",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    registration = Registration(
        student_number="S77777777",
        registration_status="approved"
    )
    db_session.add(registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/registrations/student/S77777777", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == "S77777777"

def test_student_cannot_access_other_registration(client, db_session):
    student_user = User(
        username="S88888888",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    registration = Registration(
        student_number="S99999999",
        registration_status="approved"
    )
    db_session.add(registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/registrations/student/S99999999", headers=headers)
    assert response.status_code == 403

def test_filter_registrations_by_status(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    registration1 = Registration(
        student_number="S10101010",
        registration_status="pending"
    )
    registration2 = Registration(
        student_number="S20202020",
        registration_status="approved"
    )
    db_session.add_all([registration1, registration2])
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/registrations/?status=pending", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["registration_status"] == "pending"

def test_duplicate_registration_error(client, db_session):
    admin_user = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    existing_registration = Registration(
        student_number="S12121212",
        registration_status="approved"
    )
    db_session.add(existing_registration)
    db_session.commit()
    
    token = create_access_token(data={"sub": admin_user.username, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    registration_data = {
        "student_number": "S12121212",
        "registration_status": "pending"
    }
    
    response = client.post("/api/v1/registrations/", json=registration_data, headers=headers)
    assert response.status_code == 400
    assert "Registration already exists" in response.json()["detail"]
