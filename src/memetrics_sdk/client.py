from typing import Literal
import os

import httpx


class LambdaClient:
    def __init__(self) -> None:
        self.api_key = os.environ["MONGODB_API_KEY"]
        self.url = os.environ["MONGODB_URL"]
        self.headers = {
            "Content-Type": "application/json",
            "Access-Control-Request-Headers": "*",
            "api-key": self.api_key,
        }

    def insert_one(self, document: dict) -> None:
        payload = {
            "collection": "searchresult",
            "database": "datasources-osf",
            "dataSource": "wingman-prod",
            "document": document,
        }
        with httpx.Client() as client:
            client.post(self.url, headers=self.headers, json=payload)


class Memetrics:
    """
    Allow user to interact with the Memetrics API.

    backend: lambda or microservice.
    """
    def __init__(self, backend: Literal["lambda", "microservice"] = "lambda"):
        self.backend = backend
        if self.backend == "lambda":
            self.client = LambdaClient()
