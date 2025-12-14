"""
API smoke tests
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/public/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_signup_endpoint():
    """Test user signup"""
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "resident"
    })

    # May fail if user already exists, but endpoint should respond
    assert response.status_code in [200, 400]


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


def test_protected_endpoint_without_auth():
    """Test that protected endpoints require authentication"""
    response = client.get("/resident/profile")
    assert response.status_code == 403  # Forbidden without auth


def test_submit_lead():
    """Test submitting a pilot program lead"""
    response = client.post("/public/leads", json={
        "org_name": "Test Co-Living",
        "contact_name": "John Doe",
        "contact_email": "john@testcoliving.com",
        "property_count": 5,
        "unit_count": 50
    })

    assert response.status_code == 200
    assert "message" in response.json()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
