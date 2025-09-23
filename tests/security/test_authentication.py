import pytest
from fastapi.testclient import TestClient

from ordo.config import settings
from ordo.main import app

TEST_API_TOKEN = settings.ORDO_API_TOKEN

client = TestClient(app)

def test_protected_route_no_token():
    """Verify that a request without a token to a protected route fails."""
    response = client.get("/protected")
    assert response.status_code == 401
    json_response = response.json()
    assert json_response["error_code"] == "UNAUTHORIZED"
    assert "Invalid or missing API token" in json_response["message"]

def test_protected_route_invalid_token():
    """Verify that a request with an invalid token to a protected route fails."""
    response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    json_response = response.json()
    assert json_response["error_code"] == "UNAUTHORIZED"

def test_protected_route_valid_token():
    """Verify that a request with a valid token to a protected route succeeds."""
    response = client.get("/protected", headers={"Authorization": f"Bearer {TEST_API_TOKEN}"})
    assert response.status_code == 200
    assert response.json() == {"message": "You have accessed a protected route."}

def test_unprotected_docs_route_no_token():
    """Verify that the /docs endpoint is accessible without a token."""
    response = client.get("/docs")
    # Test client follows redirects, so we expect 200 for the HTML docs page
    assert response.status_code == 200

def test_unprotected_openapi_route_no_token():
    """Verify that the /openapi.json endpoint is accessible without a token."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

def test_health_check_with_valid_token():
    """Verify that the health check works even with a token (it's not rejected)."""
    response = client.get("/health", headers={"Authorization": f"Bearer {TEST_API_TOKEN}"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}