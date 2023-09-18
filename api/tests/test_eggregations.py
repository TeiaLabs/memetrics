from fastapi.testclient import TestClient

import pytest
from pymongo.database import Database


def test_read_many(
    client: TestClient,
    headers: dict[str, str],
    db: Database,
):
    # Prepare test data
    event_data = {
        "action": "verb.specifying.what.the.user.did",
        "app": "/org/namespace/app-name",
        "app_version": "1.2.3",
        "type": "location.where.event.was.triggered.in.app",
        "user": {"email": "user@org.com"},
    }
    client.post("/events", json=event_data, headers=headers)

    # Make the request
    response = client.get(
        "/eggregations/count-by-user",
        headers=headers,
        params={
            "app": "/org/namespace/app-name",
            "date:gte": "2021-01-01",
            "date:lt": "2024-01-01",
            "$groupby": "day",
            "$limit": 10,
            "$offset": 0,
            "$sort": "-date,-count,+app",
            "type": "location.where.event.was.triggered.in.app",
            "user_email": ["user@org.com"],
        },
    )
    res_data = response.json()
    print(res_data)
    assert response.status_code == 200
    assert isinstance(res_data, list)
    assert len(res_data) == 1
    assert "date" in res_data[0]
    assert "count" in res_data[0]
    assert "app" in res_data[0]
    # Cleanup
    db["events"].delete_one({"data.app": "/org/namespace/app-name"})
    db["events_per_user"].delete_many({"data.app": "/org/namespace/app-name"})
