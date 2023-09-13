import os

import pytest
import dotenv
from fastapi.testclient import TestClient
from pymongo.database import Database

from memetrics.settings import Settings
from memetrics.app import create_app
from memetrics.utils import DB

Settings.Config.env_file = ".env.test"
dotenv.load_dotenv(".env.test")


@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def headers() -> dict[str, str]:
    data = {
        "Authorization": f"Bearer {os.environ['TEIA_API_KEY']}",
        "X-User-Email": "test@org.com",
    }
    return data


def test_health(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def db() -> Database:
    return DB.get()
