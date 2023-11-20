import os
import json
from datetime import datetime

from typing import Optional, cast

import httpx
from memetrics.events.schemas import GeneratedFields

from .schemas import TAuthHeaders, EventData


class WebserviceClient:
    def __init__(
        self,
        url: str = os.environ["MEMETRICS_URL"],
        api_key: str = os.environ["TEIA_API_KEY"],
    ):
        self.api_key = api_key
        self.url = url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.http_client = httpx.Client(
            base_url=self.url,
            headers=self.headers,
        )

    def insert_one(
        self, document: EventData, headers: Optional[TAuthHeaders] = None
    ) -> GeneratedFields:
        relative_url = "/events"
        response = self.http_client.post(
            relative_url,
            headers=cast(dict[str, str], headers),
            json=document,
        )
        response.raise_for_status()
        return response.json()

    def insert_many(
        self, documents: list[EventData], headers: Optional[TAuthHeaders] = None
    ):
        relative_url = "/events"
        data = [
            {
                "op": "add",
                "value": doc.dict(),
            }
            for doc in documents
        ]
        response = self.http_client.patch(
            relative_url,
            headers=cast(dict[str, str], headers),
            data=json.dumps(data),
        )
        response.raise_for_status()
        return response.json()

    def __del__(self):
        self.http_client.close()


class EggregatorClient:
    def __init__(self):
        self.api_key = os.environ["TEIA_API_KEY"]
        self.url = os.environ["MEMETRICS_URL"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.http_client = httpx.Client(
            base_url=self.url,
            headers=self.headers,
        )

    def read_count_by_user(
        self,
        user_email: list[str],
        action: str = None,
        app: str = None,
        date_gte: datetime = None,
        date_lt: datetime = None,
        groupby: str = "day",
        limit: int = 10,
        offset: int = 0,
        sort: str = "-count",
        type: str = None,
        headers: Optional[TAuthHeaders] = None,
    ) -> EventData:
        relative_url = "/eggregations/count-by-user"

        params = {
            "user_email": user_email,
        }

        if action:
            params["action"] = action
        if app:
            params["app"] = app
        if date_gte:
            params["date:gte"] = date_gte
        if date_lt:
            params["date:lt"] = date_lt
        if type:
            params["type"] = type

        if groupby:
            params["$groupby"] = groupby
        if limit:
            params["$limit"] = limit
        if offset:
            params["$offset"] = offset
        if sort:
            params["$sort"] = sort

        response = self.http_client.get(
            relative_url,
            headers=cast(dict[str, str], headers),
            params=params,
        )
        response.raise_for_status()
        return response.json()
