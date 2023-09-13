import os
import json

from typing import Optional, cast

import httpx
from memetrics.events.schemas import EventData, GeneratedFields

from .schemas import TAuthHeaders


class WebserviceClient:
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

    def insert_one(
        self, document: EventData, headers: Optional[TAuthHeaders] = None
    ) -> GeneratedFields:
        relative_url = "/events"
        response = self.http_client.post(
            relative_url,
            headers=cast(dict[str, str], headers),
            data=document.json(),
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
