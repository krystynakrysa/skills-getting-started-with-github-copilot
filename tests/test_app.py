import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore original participants after each test to avoid state leakage."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, participants in original.items():
        activities[name]["participants"] = participants


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_all_activities():
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(activities)


def test_get_activities_contains_expected_fields():
    response = client.get("/activities")
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]


def test_signup_adds_participant():
    client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/Unknown Activity/signup?email=x@mergington.edu")
    assert response.status_code == 404


def test_signup_duplicate_rejected():
    email = "michael@mergington.edu"  # already in Chess Club
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


# --- DELETE /activities/{activity_name}/signup ---

def test_unregister_success():
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    assert "michael@mergington.edu" in response.json()["message"]


def test_unregister_removes_participant():
    client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Unknown Activity/signup?email=x@mergington.edu")
    assert response.status_code == 404


def test_unregister_participant_not_found():
    response = client.delete("/activities/Chess Club/signup?email=nobody@mergington.edu")
    assert response.status_code == 404
