import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def reset_activities():
    # Helper to reset the in-memory DB for test isolation
    for activity in activities.values():
        if isinstance(activity.get("participants"), list):
            activity["participants"] = activity["participants"][:2]  # Reset to initial 2 participants

def test_list_activities():
    # Arrange
    reset_activities()
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert "participants" in data["Chess Club"]

def test_signup_for_activity():
    # Arrange
    reset_activities()
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]

    # Act: Try duplicate signup
    response_dup = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response_dup.status_code == 400
    assert "already signed up" in response_dup.json()["detail"]

def test_remove_participant():
    # Arrange
    reset_activities()
    activity = "Chess Club"
    email = activities[activity]["participants"][0]
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]

    # Act: Try removing again
    response_missing = client.delete(f"/activities/{activity}/participants/{email}")
    # Assert
    assert response_missing.status_code == 404
    assert "not found" in response_missing.json()["detail"]
