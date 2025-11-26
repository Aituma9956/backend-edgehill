from app.models.user import User
from app.models.student import Student
from app.core.security import create_access_token, get_password_hash

def test_create_student(client, db_session):
    admin = User(
        username="admin",
        email="admin@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin)
    db_session.commit()

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    student_data = {
        "student_number": "EH2024001",
        "forename": "John",
        "surname": "Doe",
        "cohort": "2024",
        "course_code": "PHD001",
        "programme_of_study": "Computer Science PhD",
        "mode": "Full-time",
        "international_student": False
    }
    
    response = client.post("/api/v1/students/", json=student_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == student_data["student_number"]
    assert data["forename"] == student_data["forename"]
    assert data["surname"] == student_data["surname"]

def test_get_students(client, db_session):
    admin = User(
        username="admin2",
        email="admin2@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin)
    db_session.commit()

    student1 = Student(
        student_number="EH2024002",
        forename="Jane",
        surname="Smith",
        cohort="2024",
        programme_of_study="Psychology PhD"
    )
    student2 = Student(
        student_number="EH2024003",
        forename="Bob",
        surname="Johnson",
        cohort="2024",
        programme_of_study="Biology PhD"
    )
    db_session.add(student1)
    db_session.add(student2)
    db_session.commit()

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/students/", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) >= 2
    student_numbers = [s["student_number"] for s in data]
    assert "EH2024002" in student_numbers
    assert "EH2024003" in student_numbers

def test_get_student_by_number(client, db_session):
    student = Student(
        student_number="EH2024004",
        forename="Alice",
        surname="Brown",
        cohort="2024",
        programme_of_study="Chemistry PhD"
    )
    db_session.add(student)
    db_session.commit()

    admin = User(
        username="admin3",
        email="admin3@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin)
    db_session.commit()

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/students/EH2024004", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["student_number"] == "EH2024004"
    assert data["forename"] == "Alice"
    assert data["surname"] == "Brown"

def test_student_access_control(client, db_session):
    student_user = User(
        username="EH2024005",
        email="student@edgehill.ac.uk",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db_session.add(student_user)
    db_session.commit()

    student = Student(
        student_number="EH2024005",
        forename="Student",
        surname="Test",
        cohort="2024"
    )
    db_session.add(student)
    db_session.commit()

    other_student = Student(
        student_number="EH2024006",
        forename="Other",
        surname="Student",
        cohort="2024"
    )
    db_session.add(other_student)
    db_session.commit()

    token = create_access_token(data={"sub": student_user.username, "role": student_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/students/EH2024005", headers=headers)
    assert response.status_code == 200

    response = client.get("/api/v1/students/EH2024006", headers=headers)
    assert response.status_code == 403

def test_update_student(client, db_session):
    admin = User(
        username="admin4",
        email="admin4@edgehill.ac.uk",
        hashed_password=get_password_hash("admin123"),
        role="system_admin"
    )
    db_session.add(admin)
    db_session.commit()

    student = Student(
        student_number="EH2024007",
        forename="Update",
        surname="Test",
        cohort="2024",
        mode="Part-time"
    )
    db_session.add(student)
    db_session.commit()

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "mode": "Full-time",
        "programme_of_study": "Updated PhD Programme"
    }
    
    response = client.put("/api/v1/students/EH2024007", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["mode"] == "Full-time"
    assert data["programme_of_study"] == "Updated PhD Programme"
    assert data["forename"] == "Update"
