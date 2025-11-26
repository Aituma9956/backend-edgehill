from app.models.user import User
from app.core.security import create_access_token, get_password_hash

def test_register_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@edgehill.ac.uk",
        "password": "testpassword123",
        "role": "student",
        "first_name": "Test",
        "last_name": "User",
        "department": "Computer Science"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data

def test_login_user(client, db_session):
    hashed_password = get_password_hash("testpassword123")
    user = User(
        username="logintest",
        email="logintest@edgehill.ac.uk",
        hashed_password=hashed_password,
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "username": "logintest",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/token", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(client, db_session):
    user = User(
        username="currentuser",
        email="current@edgehill.ac.uk",
        hashed_password=get_password_hash("password123"),
        role="student",
        first_name="Current",
        last_name="User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": user.username, "role": user.role})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["role"] == user.role

def test_invalid_credentials(client):
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/token", json=login_data)
    assert response.status_code == 401

def test_duplicate_username(client):
    user1_data = {
        "username": "duplicate",
        "email": "first@edgehill.ac.uk",
        "password": "password123",
        "role": "student"
    }
    
    response1 = client.post("/api/v1/auth/register", json=user1_data)
    assert response1.status_code == 200

    user2_data = {
        "username": "duplicate",
        "email": "second@edgehill.ac.uk",
        "password": "password123",
        "role": "student"
    }
    
    response2 = client.post("/api/v1/auth/register", json=user2_data)
    assert response2.status_code == 400
    assert "Username already registered" in response2.json()["detail"]
