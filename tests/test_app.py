from fastapi.testclient import TestClient
from urllib.parse import quote
import copy

from src.app import app, activities


client = TestClient(app)


def setup_function():
    # make a deep copy so tests can modify activities safely
    global _orig_activities
    _orig_activities = copy.deepcopy(activities)


def teardown_function():
    # restore original activities after each test
    activities.clear()
    activities.update(copy.deepcopy(_orig_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    email = "test.user@example.com"
    path = f"/activities/{quote('Chess Club')}/signup"
    resp = client.post(path, params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_already_signed():
    # use an existing participant from the fixture data
    existing = _orig_activities["Chess Club"]["participants"][0]
    path = f"/activities/{quote('Chess Club')}/signup"
    resp = client.post(path, params={"email": existing})
    assert resp.status_code == 400


def test_signup_nonexistent_activity():
    email = "nobody@example.com"
    path = f"/activities/{quote('No Such Activity')}/signup"
    resp = client.post(path, params={"email": email})
    assert resp.status_code == 404
