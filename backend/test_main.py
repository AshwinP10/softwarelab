import pytest
from fastapi.testclient import TestClient
from main import app
import json
import os

client = TestClient(app)

# Clean up test files before each test
@pytest.fixture(autouse=True)
def cleanup_test_files():
    test_files = ['users.json', 'projects.json', 'hardware.json', 'checkouts.json']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    yield
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "HaaS API is running"}

def test_signup():
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_signup_duplicate_email():
    # First signup
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    
    # Second signup with same email
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login():
    # First signup
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    
    # Then login
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    # First signup
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    
    # Login with wrong password
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401

def get_auth_headers():
    # Helper function to get auth headers
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_project():
    headers = get_auth_headers()
    
    response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test project"
    assert "id" in data

def test_get_projects():
    headers = get_auth_headers()
    
    # Create a project first
    client.post(
        "/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    
    # Get projects
    response = client.get("/projects", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Project"

def test_get_hardware():
    headers = get_auth_headers()
    
    response = client.get("/hardware", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(hw["name"] == "HWSet1" for hw in data)
    assert any(hw["name"] == "HWSet2" for hw in data)

def test_checkout_hardware():
    headers = get_auth_headers()
    
    # Create a project first
    project_response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Checkout hardware
    response = client.post(
        "/hardware/checkout",
        json={
            "hardware_set_id": "hwset1",
            "project_id": project_id,
            "quantity": 2
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "Checked out 2 units" in response.json()["message"]

def test_checkin_hardware():
    headers = get_auth_headers()
    
    # Create a project first
    project_response = client.post(
        "/projects",
        json={"name": "Test Project", "description": "A test project"},
        headers=headers
    )
    project_id = project_response.json()["id"]
    
    # Checkout hardware first
    client.post(
        "/hardware/checkout",
        json={
            "hardware_set_id": "hwset1",
            "project_id": project_id,
            "quantity": 2
        },
        headers=headers
    )
    
    # Then check it back in
    response = client.post(
        "/hardware/checkin",
        json={
            "hardware_set_id": "hwset1",
            "project_id": project_id,
            "quantity": 1
        },
        headers=headers
    )
    assert response.status_code == 200
    assert "Checked in 1 units" in response.json()["message"]

def test_unauthorized_access():
    # Try to access protected endpoint without auth
    response = client.get("/projects")
    assert response.status_code == 401
