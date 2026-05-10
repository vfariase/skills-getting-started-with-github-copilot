import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Helper to reset activities state for each test (since in-memory DB)
def reset_activities():
    app.dependency_overrides = {}
    for activity in app.routes[2].endpoint.__globals__["activities"].values():
        if "participants" in activity:
            activity["participants"] = []

@pytest.fixture(autouse=True)
def run_around_tests():
    reset_activities()
    yield
    reset_activities()

def test_get_activities():
    # Arrange
    # (No setup needed, just fetch)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_signup_participant():
    # Arrange
    activity = "Chess Club"
    email = "test1@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

def test_signup_duplicate_participant():
    # Arrange
    activity = "Chess Club"
    email = "test2@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "test3@mergington.edu"
    client.post(f"/activities/{activity}/signup?email={email}")
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]

def test_remove_nonexistent_participant():
    # Arrange
    activity = "Chess Club"
    email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_signup_nonexistent_activity():
    # Arrange
    activity = "Nonexistent Club"
    email = "test4@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
