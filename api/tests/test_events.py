from fastapi.testclient import TestClient

import pytest
from bson import ObjectId
from pymongo.database import Database


@pytest.fixture(scope="module")
def event_data() -> dict:
    data = {
        "action": "verb.specifying.what.the.user.did",
        "app": "/org/namespace/app-name",
        "app_version": "1.2.3",
        "type": "location.where.event.was.triggered.in.app",
        "user": {"email": "user@org.com"},
    }
    return data


def test_post(client: TestClient, headers: dict[str, str], db: Database, event_data):
    response = client.post("/events", json=event_data, headers=headers)
    res_data = response.json()
    print(res_data)
    assert response.status_code == 201
    assert "_id" in res_data
    assert "created_at" in res_data
    assert "created_by" in res_data
    doc = db["events"].find_one({"_id": ObjectId(res_data["_id"])})
    assert doc is not None
    assert doc["data"]["action"] == event_data["action"]
    assert doc["data"]["app"] == event_data["app"]
    assert doc["data"]["app_version"] == event_data["app_version"]
    assert doc["data"]["type"] == event_data["type"]
    assert doc["data"]["user"] == event_data["user"]
    assert doc["created_by"]["user_email"] == headers["X-User-Email"]
    # cleanup
    db["events"].delete_one({"_id": ObjectId(res_data["_id"])})
