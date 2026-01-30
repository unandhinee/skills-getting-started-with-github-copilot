import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    # snapshot and restore in-memory activities to keep tests isolated
    original = copy.deepcopy(app_module.activities)
    client = TestClient(app_module.app)
    yield client
    app_module.activities = original


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect at least one known activity from the seed data
    assert "Soccer Team" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    test_email = "teststudent@example.com"

    # Ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert test_email not in resp.json()[activity]["participants"]

    # Sign up
    res = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert res.status_code == 200
    assert test_email in client.get("/activities").json()[activity]["participants"]

    # Duplicate signup should fail
    res_dup = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert res_dup.status_code == 400

    # Unregister
    res_unreg = client.delete(f"/activities/{activity}/unregister?email={test_email}")
    assert res_unreg.status_code == 200
    assert test_email not in client.get("/activities").json()[activity]["participants"]

    # Unregistering again should return 404
    res_unreg_again = client.delete(f"/activities/{activity}/unregister?email={test_email}")
    assert res_unreg_again.status_code == 404
