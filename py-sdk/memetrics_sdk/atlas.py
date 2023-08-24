import os
from typing import Any

import httpx


class AtlasClient():
    def __init__(self):
        self.api_key = os.environ["MONGODB_API_KEY"]
        self.cluster_name = os.environ["MONGODB_CLUSTER"]
        self.url = os.environ["MONGODB_URL"]
        self.headers = {
            "Content-Type": "application/json",
            "Access-Control-Request-Headers": "*",
            "api-key": self.api_key,
        }
        self.http_client = httpx.Client(base_url=self.url, headers=self.headers)

    def insert_one(self, document: dict[str, Any], db_name: str = "memetrics") -> str:
        relative_url = "/insertOne"
        payload = {
            "collection": "events",
            "database": db_name,
            "dataSource": self.cluster_name,
            "document": document,
        }
        res = self.http_client.post(relative_url, json=payload)
        res_json = res.json()
        return res_json["insertedId"]

    def __del__(self):
        self.http_client.close()
