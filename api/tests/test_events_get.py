from fastapi.testclient import TestClient

import pytest
from pymongo.database import Database


@pytest.fixture(scope="module")
def event_data():
    data = [
        {
            "action": "verb.specifying.what.the.user.did",
            "app": "/org/namespace/app-name",
            "app_version": "1.2.3",
            "type": "location.where.event.was.triggered.in.app",
            "user": {"email": "user@org.com"},
        },
        {
            "action": "another.verb",
            "app": "/org/namespace/app-name",
            "app_version": "1.2.3",
            "type": "location.where.event.was.triggered.in.app",
            "user": {"email": "user2@org.com"},
        }
    ]
    return data


@pytest.fixture(scope="module", autouse=True)
def saved_events_ids(client: TestClient, event_data: dict, headers):
    ids = []
    for event in event_data:
        response = client.post("/events", json=event, headers=headers)
        res_data = response.json()
        ids.append(res_data["_id"])
    return ids



def test_get_events_with_action_and_app(client: TestClient, headers: dict[str, str], db: Database, saved_events_ids: list[str]):
    query_params = {
        "data.action": "verb.specifying.what.the.user.did",
        "data.app": "/org/namespace/app-name"
    }
    response = client.get("/events", params=query_params, headers=headers)
    res_data = response.json()
    print(res_data)
    assert response.status_code == 200
    assert isinstance(res_data, list)
    assert len(res_data) > 0  # Check if there are events returned
    for event in res_data:
        assert "data" in event
        assert "action" in event["data"]
        assert event["data"]["action"] == "verb.specifying.what.the.user.did"
        assert "app" in event["data"]
        assert event["data"]["app"] == "/org/namespace/app-name"
    # cleanup
    db.events.delete_many({"_id": {"$in": saved_events_ids}})


def test_get_events_with_identifier(client: TestClient, headers: dict[str, str], db: Database, saved_events_ids: list[str]):
    query_params = {
        "_id": saved_events_ids[0]
    }
    response = client.get("/events", params=query_params, headers=headers)
    res_data = response.json()
    print(res_data)
    assert response.status_code == 200
    assert isinstance(res_data, list)
    assert len(res_data) == 1  # Check if only one event is returned
    event = res_data[0]
    assert "_id" in event
    assert event["_id"]["$oid"] == saved_events_ids[0]
    # cleanup
    db.events.delete_many({"_id": {"$in": saved_events_ids}})


def test_get_events_with_sorting_and_limit(client: TestClient, headers: dict[str, str], db: Database, saved_events_ids: list[str]):
    query_params = {
        "$sort": "-created_at",
        "$limit": 2
    }
    response = client.get("/events", params=query_params, headers=headers)
    res_data = response.json()
    print(res_data)
    assert response.status_code == 200
    assert isinstance(res_data, list)
    assert len(res_data) <= 2  # Check if the number of events returned is less than or equal to 2
    if len(res_data) > 1:
        for i in range(len(res_data) - 1):
            assert res_data[i]["created_at"] >= res_data[i + 1]["created_at"]
    # cleanup
    db.events.delete_many({"_id": {"$in": saved_events_ids}})
