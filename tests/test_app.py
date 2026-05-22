"""
Tests for the Mergington High School API backend.

These use the Arrange-Act-Assert pattern and a TestClient for FastAPI.
"""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset app state between tests."""
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_dict(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, dict)
        assert expected_activity in json_data
        assert "description" in json_data[expected_activity]
        assert "schedule" in json_data[expected_activity]
        assert "participants" in json_data[expected_activity]


class TestSignupForActivity:
    def test_signup_for_activity_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

    def test_signup_normalizes_email(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "NEWSTUDENT@MERGINGTON.EDU"
        normalized = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        assert normalized in activities_response.json()[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_activity_at_capacity_returns_400(self, client):
        # Arrange
        activity_name = "Soccer Club"
        activities[activity_name]["max_participants"] = 1
        activities[activity_name]["participants"] = ["existing@mergington.edu"]
        email = "new@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]


class TestRemoveParticipant:
    def test_remove_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_remove_participant_normalizes_email(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "MICHAEL@MERGINGTON.EDU"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        activities_response = client.get("/activities")
        assert "michael@mergington.edu" not in activities_response.json()[activity_name]["participants"]

    def test_remove_participant_not_found_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notfound@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_participant_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


def test_root_redirects_to_index(client):
    # Arrange / Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
